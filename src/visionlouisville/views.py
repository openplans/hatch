import json
from django.template.defaultfilters import truncatechars
from django.views.generic import TemplateView, DetailView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.http import Http404
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import APIException
from .models import Reply, User, Vision
from .serializers import ReplySerializer, UserSerializer, VisionSerializer
from .services import default_twitter_service


class AppMixin (object):
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

    def get_vision_url(self, request, vision):
        return request.build_absolute_uri(
            '/visions/%s' % vision.pk)
            # reverse('vision-detail', kwargs={'pk': self.pk}))

    def get_context_data(self, **kwargs):
        context = super(AppMixin, self).get_context_data(**kwargs)

        context['NS'] = 'VisionLouisville'

        if self.request.user.is_authenticated():
            user = self.request.user
            serializer = UserSerializer(user)
            serializer.context = {
                'twitter_service': self.get_twitter_service(),
                'requesting_user': self.get_requesting_user(),
            }
            user_data = serializer.data
            context['user_data'] = user_data
            context['user_json'] = json.dumps(user_data)
        else:
            context['user_json'] = '{}'

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


# API
class TweetException (APIException):
    status_code = 400


class VisionViewSet (AppMixin, ModelViewSet):
    model = Vision
    serializer_class = VisionSerializer

    def get_queryset(self):
        queryset = Vision.objects.all()\
            .select_related('author')\
            .prefetch_related('author__social_auth')

        category = self.request.GET.get('category')
        if (category):
            queryset = queryset.filter(category__iexact=category)

        return queryset

    def get_app_tweet_text(self, request, vision):
        vision_url = self.get_vision_url(request, vision)
        category = vision.category.lower()
        username = vision.author.username

        return \
            'Check out this vision about %s in Louisville, from @%s: %s' % (
                category, username, vision_url)

    def get_user_tweet_text(self, request, vision):
        vision_url = self.get_vision_url(request, vision)
        return vision.title + ' ' + vision_url

    def post_save(self, vision, created):
        """
        This is called in the create handler, after the serializer saves the
        vision.
        """
        if created:
            # Always tweet with the app's account
            tweet_text = self.get_app_tweet_text(self.request, vision)
            service = self.get_twitter_service()
            success, response = service.tweet(tweet_text)

            if success:
                vision.tweet_id = response['id']
                vision.save()
            else:
                raise TweetException('App tweet not sent: ' + response)

            # Also tweet from user's account if requested
            if self.request.META.get('HTTP_X_SEND_TO_TWITTER', False):
                success, response = service.tweet(tweet_text,
                                                  self.request.user)
                if not success:
                    raise TweetException('User tweet not sent: ' + response)


class ReplyViewSet (ModelViewSet):
    model = Reply
    serializer_class = ReplySerializer

    def get_tweet_text(self, request, reply):
        app_username = settings.TWITTER_USERNAME
        if not app_username.startswith('@'):
            app_username = '@' + app_username

        if app_username not in reply.content:
            tweet_text = app_username + ' ' + reply.content
        else:
            tweet_text = reply.content

        return truncatechars(tweet_text, 140)


class UserViewSet (AppMixin, ModelViewSet):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Only get users that have an associated social media account.
        """
        queryset = User.objects\
            .annotate(social_count=Count('social_auth'))\
            .filter(social_count__gt=0)
        return queryset


class CurrentUserAPIView (AppMixin, RetrieveAPIView):
    model = User
    serializer_class = UserSerializer

    def get_object(self):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            raise Http404('No user is logged in.')

# Views
app_view = AppView.as_view()
vision_instance_view = VisionInstanceView.as_view()
current_user_api_view = CurrentUserAPIView.as_view()

# Setup the API routes
api_router = DefaultRouter()
api_router.register('visions', VisionViewSet)
api_router.register('users', UserViewSet)
api_router.register('replies', ReplyViewSet)
