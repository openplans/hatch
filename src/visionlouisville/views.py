from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.http import Http404
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView
from .models import User, Vision
from .serializers import UserSerializer, VisionSerializer
from .services import TwitterService


class EnsureCSRFCookieMixin (object):
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super(EnsureCSRFCookieMixin, self).dispatch(request, *args, **kwargs)


# App
class AppView (EnsureCSRFCookieMixin, TemplateView):
    template_name = 'visionlouisville/index.html'


# API
class VisionViewSet (ModelViewSet):
    model = Vision
    serializer_class = VisionSerializer

    def get_serializer_context(self):
        context = super(VisionViewSet, self).get_serializer_context()
        context['twitter_service'] = TwitterService()

    def get_queryset(self):
        queryset = Vision.objects.all()\
            .select_related('author')\
            .prefetch_related('author__social_auth')

        category = self.request.GET.get('category')
        if (category):
            queryset = queryset.filter(category__iexact=category)

        return queryset

    def create(self, request, *args, **kwargs):
        result = super(VisionViewSet, self).create(request, *args, **kwargs)

        if result.status_code == 201 and request.META['HTTP_X_SEND_TO_TWITTER']:
            tweet_text = self.object.get_tweet_text(request)
            service = TwitterService()
            service.tweet(tweet_text)

        return result


class UserViewSet (ModelViewSet):
    model = User
    serializer_class = UserSerializer

    def get_serializer_context(self):
        context = super(UserViewSet, self).get_serializer_context()
        context['twitter_service'] = TwitterService()

    def get_queryset(self):
        queryset = User.objects\
            .annotate(social_count=Count('social_auth'))\
            .filter(social_count__gt=0)
        return queryset


class CurrentUserAPIView (RetrieveAPIView):
    model = User
    serializer_class = UserSerializer

    def get_object(self):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            raise Http404('No user is logged in.')

# Views
app_view = AppView.as_view()
current_user_api_view = CurrentUserAPIView.as_view()

# Setup the API routes
api_router = DefaultRouter()
api_router.register('visions', VisionViewSet)
api_router.register('users', UserViewSet)
