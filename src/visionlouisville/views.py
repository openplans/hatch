# -*- coding: utf-8 -*-

import json
from django.conf import settings
from django.template.defaultfilters import truncatechars
from django.views.generic import TemplateView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.utils.text import Truncator
from django.db.models import Count
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.utils.encoders import JSONEncoder
from .models import Reply, User, Vision, Category, Tweet, AppConfig
from .forms import SecretAllySignupForm
from .serializers import (
    ReplySerializer, UserSerializer, VisionSerializer, CategorySerializer,
    MinimalVisionSerializer, AppConfigSerializer)
from .services import default_twitter_service


class AppMixin (object):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @classmethod
    def get_twitter_service(self):
        return default_twitter_service

    def get_requesting_user(self):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            return None

    def get_serializer_context(self):
        context = super(AppMixin, self).get_serializer_context()
        context['twitter_service'] = self.get_twitter_service()
        context['requesting_user'] = self.get_requesting_user()
        return context

    @classmethod
    def get_vision_url(cls, request, vision):
        return request.build_absolute_uri(
            '/visions/%s' % vision.pk)
            # reverse('vision-detail', kwargs={'pk': self.pk}))

    def get_vision_queryset(self, base_queryset=None):
        return (base_queryset or Vision.objects.all())\
            .select_related('author')\
            .prefetch_related('author__social_auth')\
            .prefetch_related('author__groups')\
            .prefetch_related('replies')\
            .prefetch_related('replies__author__social_auth')\
            .prefetch_related('replies__author__groups')\
            .prefetch_related('supporters')\
            .prefetch_related('supporters__social_auth')\
            .prefetch_related('supporters__groups')\
            .prefetch_related('sharers')

    def get_user_queryset(self, base_queryset=None):
        return (base_queryset or User.objects.all())\
            .annotate(social_count=Count('social_auth'))\
            .filter(social_count__gt=0)\
            .prefetch_related('visions')\
            .prefetch_related('visions__supporters')\
            .prefetch_related('replies')\
            .prefetch_related('replies__vision__author__social_auth')\
            .prefetch_related('replies__vision__supporters')\
            .prefetch_related('supported')\
            .prefetch_related('supported__author__social_auth')\
            .prefetch_related('supported__supporters')\
            .prefetch_related('social_auth')\
            .prefetch_related('groups')

    def get_category_queryset(self, base_queryset=None):
        return (base_queryset or Category.objects.all())

    def get_context_data(self, **kwargs):
        context = super(AppMixin, self).get_context_data(**kwargs)
        service = self.get_twitter_service()

        if self.request.user.is_authenticated():
            user_qs = self.get_user_queryset(
                User.objects.filter(pk=self.request.user.pk))

            try:
                user = user_qs.get()
            except User.DoesNotExist:
                user = None
        else:
            user = None

        context['NS'] = 'VisionLouisville'
        context['twitter_config'] = json.dumps(service.get_config(user))

        category_query = self.get_category_queryset()
        context['categories'] = json.dumps(CategorySerializer(category_query).data)

        app_config_query = AppConfig.objects.all()[:1]
        context['app'] = app_config_query[0]
        context['app_json'] = json.dumps(AppConfigSerializer(app_config_query[0]).data)

        if user:
            serializer = UserSerializer(user)
            serializer.context = {
                'twitter_service': self.get_twitter_service(),
                'requesting_user': self.get_requesting_user(),
            }
            user_data = serializer.data
            context['user_data'] = user_data
            context['user_json'] = json.dumps(user_data, cls=JSONEncoder)
        else:
            context['user_json'] = 'null'

        return context


class EnsureCSRFCookieMixin (object):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super(EnsureCSRFCookieMixin, self).dispatch(
            request, *args, **kwargs)


# App
class AppView (AppMixin, EnsureCSRFCookieMixin, TemplateView):
    template_name = 'visionlouisville/index.html'


class VisionInstanceView (AppMixin, EnsureCSRFCookieMixin, DetailView):
    template_name = 'visionlouisville/index.html'
    model = Vision
    context_object_name = 'vision'


class CategoryInstanceView (AppMixin, EnsureCSRFCookieMixin, DetailView):
    template_name = 'visionlouisville/index.html'
    model = Category
    context_object_name = 'category'


class SecretAllySignupView (AppMixin, EnsureCSRFCookieMixin, FormView):
    template_name = 'visionlouisville/index.html'
    form_class = SecretAllySignupForm

    def get_success_url(self):
        return self.request.get_full_path()

    def form_valid(self, form):
        user = self.request.user
        if user.is_authenticated():
            user.email = form.cleaned_data['email']
            user.add_to_group('allies')
            user.save()
        return super(SecretAllySignupView, self).form_valid(form)


# API
class TweetException (APIException):
    status_code = 400

    def __init__(self, detail):
        self.detail = detail


class VisionViewSet (AppMixin, ModelViewSet):
    model = Vision
    serializer_class = VisionSerializer

    def get_queryset(self):
        queryset = self.get_vision_queryset()

        category = self.request.GET.get('category')
        if (category):
            queryset = queryset.filter(category__iexact=category)

        return queryset

    # TODO: Move this into the settings/config
    @classmethod
    def get_app_tweet_text(cls, request, vision):
        vision_url = cls.get_vision_url(request, vision)
        service = cls.get_twitter_service()
        username = vision.author.username
        url_length = service.get_url_length(vision_url)

        attribution = u' —@%s ' % (username,)
        vision_length = 140 - len(attribution) - url_length - 2
        return ''.join([
            '"', Truncator(vision.text).chars(vision_length, u'…'), '"',
            attribution,
            vision_url
        ])

    @classmethod
    def get_user_tweet_text(cls, request, vision):
        vision_url = cls.get_vision_url(request, vision)
        service = cls.get_twitter_service()
        url_length = service.get_url_length(vision_url)

        vision_length = 140 - url_length - 1
        return ''.join([
            truncatechars(vision.text, vision_length),
            ' ', vision_url
        ])

    @classmethod
    def tweet_vision_from_app(cls, request, vision):
        tweet_text = cls.get_app_tweet_text(request, vision)
        service = cls.get_twitter_service()
        success, response = service.tweet(tweet_text)

        if success:
            tweet, created = Tweet.objects.create_or_update_from_tweet_data(response)
            vision.tweet = tweet
            vision.save()
        else:
            raise TweetException('App tweet not sent: ' + response)

    def post_save(self, vision, created):
        """
        This is called in the create handler, after the serializer saves the
        vision. We do it _after_ saving, because we need the object's id to
        build the vision's URL to put in the tweet.
        """
        if created:
            # Always tweet with the app's account
            try:
                self.tweet_vision_from_app(self.request, vision)
            except TweetException:
                vision.delete()
                raise

            # Also tweet from user's account if requested
            if self.request.META.get('HTTP_X_SEND_TO_TWITTER', False):
                tweet_text = self.get_user_tweet_text(self.request, vision)
                service = self.get_twitter_service()
                success, response = service.tweet(tweet_text,
                                                  self.request.user)
                if not success:
                    raise TweetException('User tweet not sent: ' + response)


class ReplyViewSet (AppMixin, ModelViewSet):
    model = Reply
    serializer_class = ReplySerializer

    def get_tweet_text(self, request, reply):
        app_username = settings.TWITTER_USERNAME
        if not app_username.startswith('@'):
            app_username = '@' + app_username

        if app_username not in reply.text:
            tweet_text = app_username + ' ' + reply.text
        else:
            tweet_text = reply.text

        return truncatechars(tweet_text, 140)

    def pre_save(self, reply):
        """
        This is called in the create handler, before the serializer saves the
        reply. We do it _before_ saving so that we don't need to delete the
        model instance if the tweet fails.
        """
        if reply.pk is None:
            tweet_text = self.get_tweet_text(self.request, reply)
            service = self.get_twitter_service()
            success, response = service.tweet(
                tweet_text, self.request.user,
                in_reply_to_status_id=reply.vision.tweet_id)

            if success:
                tweet, created = Tweet.objects.create_or_update_from_tweet_data(response)
                reply.tweet = tweet
            else:
                raise TweetException('User reply not tweeted: ' + response)


class SiteMapView (AppMixin, TemplateView):
    template_name = 'visionlouisville/sitemap.xml'

    def get_visions_data(self):
        visions = self.get_vision_queryset()
        serializer = MinimalVisionSerializer(visions)
        serializer.context = {
            'twitter_service': self.get_twitter_service(),
            'requesting_user': self.get_requesting_user(),
        }

        return serializer.data

    def get_category_data(self):
        categories = self.get_category_queryset()
        serializer = CategorySerializer(categories)
        return serializer.data

    def get_context_data(self, **kwargs):
        context = super(SiteMapView, self).get_context_data(**kwargs)
        context['categories'] = self.get_category_data()
        context['visions'] = self.get_visions_data()
        return context


class UserViewSet (AppMixin, ModelViewSet):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Only get users that have an associated social media account.
        """
        queryset = self.get_user_queryset()

        not_group_names = self.request.GET.getlist('notgroup')
        if (not_group_names):
            queryset = queryset.exclude(groups__name__in=not_group_names)

        group_names = self.request.GET.getlist('group')
        if (group_names):
            queryset = queryset.filter(groups__name__in=group_names)

        visible_status = self.request.GET.get('visible_on_home', None)
        if (visible_status is not None):
            visible_status = (visible_status.lower() not in ('false', 'off', 'no'))
            queryset = queryset.filter(visible_on_home=visible_status)

        return queryset


class CurrentUserAPIView (AppMixin, RetrieveAPIView):
    model = User
    serializer_class = UserSerializer

    def get_object(self):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            raise Http404('No user is logged in.')


class VisionActionViewSet (SingleObjectMixin, AppMixin, ViewSet):
    def get_queryset(self):
        return Vision.objects.all()

    def support(self, request, *args, **kwargs):
        vision = self.get_object()
        self.request.user.support(vision)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def unsupport(self, request, *args, **kwargs):
        vision = self.get_object()
        self.request.user.unsupport(vision)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def share(self, request, *args, **kwargs):
        vision = self.get_object()
        service = self.get_twitter_service()
        success, response = service.retweet(
            vision.tweet_id, self.request.user)

        if success:
            tweet_id = response['id']
        else:
            raise TweetException('User reply not tweeted: ' + response)

        self.request.user.share(vision, tweet_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


# App views
home_app_view = AppView.as_view()
vision_detail_app_view = VisionInstanceView.as_view()
category_app_view = CategoryInstanceView.as_view()
secret_ally_signup_view = SecretAllySignupView.as_view()
robots_view = TemplateView.as_view(template_name='visionlouisville/robots.txt')
sitemap_view = SiteMapView.as_view()


# API views
current_user_api_view = CurrentUserAPIView.as_view()
support_api_view = VisionActionViewSet.as_view({'post': 'support',
                                                'put': 'support',
                                                'delete': 'unsupport'})
unsupport_api_view = VisionActionViewSet.as_view({'post': 'unsupport'})
share_api_view = VisionActionViewSet.as_view({'post': 'share'})

# Setup the API routes
api_router = DefaultRouter()
api_router.register('visions', VisionViewSet)
api_router.register('users', UserViewSet)
api_router.register('replies', ReplyViewSet)
