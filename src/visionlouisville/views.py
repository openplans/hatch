from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from .models import Vision


# App
class AppView (TemplateView):
    template_name = 'visionlouisville/index.html'


# API
class VisionViewSet (ModelViewSet):
    model = Vision

# Views
app_view = AppView.as_view()

# Setup the API routes
api_router = DefaultRouter()
api_router.register('visions', VisionViewSet)
