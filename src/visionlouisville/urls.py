from django.conf.urls import patterns, include, url
from .views import (
    home_app_view, secret_ally_signup_view, vision_detail_app_view, api_router,
    current_user_api_view, share_api_view, support_api_view, unsupport_api_view)

# Admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',

    # Social Auth
    url(r'^', include('social_auth.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/'}),
    url(r'^ally-signup$', secret_ally_signup_view, name='secret-ally-login'),

    # API
    url(r'^api/users/(?P<pk>current)/$',        current_user_api_view, name='current-user-detail'),
    url(r'^api/visions/(?P<pk>\d+)/support$',   support_api_view,      name='support-vision-action'),
    url(r'^api/visions/(?P<pk>\d+)/unsupport$', unsupport_api_view,    name='unsupport-vision-action'),
    url(r'^api/visions/(?P<pk>\d+)/share$',     share_api_view,        name='share-vision-action'),
    url(r'^api/', include(api_router.urls)),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # App
    url(r'^visions/(?P<pk>\d+)$', vision_detail_app_view,     name='app-vision-detail'),
    url(r'^',                     home_app_view,              name='app-home'),
)
