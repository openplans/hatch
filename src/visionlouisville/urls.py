from django.conf.urls import patterns, include, url
from views import app_view, api_router

# Admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # App
    url(r'^$', app_view, name='app'),

    # API
    url(r'^api/', include(api_router.urls)),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
)
