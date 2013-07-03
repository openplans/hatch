from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from .models import Vision
from .serializers import VisionSerializer


# App
class AppView (TemplateView):
    template_name = 'visionlouisville/index.html'


# API
class VisionViewSet (ModelViewSet):
    model = Vision
    serializer_class = VisionSerializer

    def get_queryset(self):
        queryset = Vision.objects.all().select_related('author').prefetch_related('author__social_auth')

        category = self.request.GET.get('category')
        if (category):
            queryset = queryset.filter(category__iexact=category)

        return queryset

# Views
app_view = AppView.as_view()

# Setup the API routes
api_router = DefaultRouter()
api_router.register('visions', VisionViewSet)
