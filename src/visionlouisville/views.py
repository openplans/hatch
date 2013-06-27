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

    def get_queryset(self):
        queryset = super(VisionViewSet, self).get_queryset()

        category = self.request.GET.get('category')
        if (category):
            queryset = queryset.filter(category__iexact=category)

        return queryset

# Views
app_view = AppView.as_view()

# Setup the API routes
api_router = DefaultRouter()
api_router.register('visions', VisionViewSet)
