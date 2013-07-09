import json
from django.views.generic import TemplateView, DetailView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.http import Http404
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView
from .models import User, Vision
from .serializers import UserSerializer, VisionSerializer
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

    def create(self, request, *args, **kwargs):
        result = super(VisionViewSet, self).create(request, *args, **kwargs)

        # Always tweet with the app's account
        if result.status_code == 201:
            tweet_text = self.get_app_tweet_text(request, self.object)
            service = TwitterService()
            service.tweet(tweet_text)

            # Also tweet from user's account if requested
            if request.META.get('HTTP_X_SEND_TO_TWITTER', False):
                service.tweet(tweet_text, self.request.user)

        return result


class UserViewSet (AppMixin, ModelViewSet):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
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
