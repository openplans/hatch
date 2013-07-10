from django.conf.urls import patterns, include, url
from .views import (app_view, api_router, current_user_api_view, 
    support_api_view, unsupport_api_view, vision_instance_view)

# Admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Social Auth
    url(r'^', include('social_auth.urls')),

    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout',
        kwargs={'next_page': '/'}),

    # API
    url(r'^api/users/(?P<pk>current)/$', current_user_api_view,
        name='current-user-detail'),
    url(r'^api/visions/(?P<pk>\d+)/support$', support_api_view,
        name='current-user-detail'),
    url(r'^api/visions/(?P<pk>\d+)/unsupport$', unsupport_api_view,
        name='current-user-detail'),
    url(r'^api/', include(api_router.urls)),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # App
    url(r'^visions/(?P<pk>\d+)$', vision_instance_view, name='vision-instance'),
    url(r'^', app_view, name='app'),
)
