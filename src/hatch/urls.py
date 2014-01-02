from django.conf.urls import patterns, include, url
from .views import (
    home_app_view, secret_ally_signup_view, vision_detail_app_view, api_router,
    current_user_api_view, share_api_view, support_api_view, unsupport_api_view,
    category_app_view, robots_view, sitemap_view, notifications_api_view)
from .models import AppConfig

# Admin
from django.contrib import admin
admin.autodiscover()


def favicon_view(request):
    from django.shortcuts import redirect
    from django.conf import settings
    return redirect(settings.STATIC_URL + 'images/favicon.png')


def vision_patterns():
    try:
        app_config = AppConfig.get()
    except IndexError:
        # This app has not been configured. Please add a
        # record to the AppConfig model to set your app-specific
        # settings.
        return patterns('')

    # App
    return patterns(
        '',
        url(r'^' + app_config.vision_plural + '/(?P<category>[^/]+)/(?P<pk>\d+)$',      vision_detail_app_view, name='app-vision-detail'),
        url(r'^' + app_config.vision_plural + '/(?P<pk>\w+)/list$', category_app_view,      name='app-vision-list'),
    )


def generate_exception_view(request):
    raise Exception('DIE!!!')

urlpatterns = (
    patterns(
        '',

        # Social Auth
        url(r'^', include('social_auth.urls')),
        url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/'}),
        url(r'^ally$', secret_ally_signup_view, name='secret-ally-login'),

        # Meta
        url(r'^robots.txt$', robots_view, name='robots'),
        url(r'^sitemap.xml$', sitemap_view, name='sitemap'),
        url(r'^favicon\..+$', favicon_view, name='favicon'),

        # Admin
        url(r'^admin/', include(admin.site.urls)),

        # API
        url(r'^api/users/(?P<pk>current)/$',        current_user_api_view,  name='current-user-detail'),
        url(r'^api/visions/(?P<pk>\d+)/support$',   support_api_view,       name='support-vision-action'),
        url(r'^api/visions/(?P<pk>\d+)/unsupport$', unsupport_api_view,     name='unsupport-vision-action'),
        url(r'^api/visions/(?P<pk>\d+)/share$',     share_api_view,         name='share-vision-action'),
        url(r'^api/notifications$',                 notifications_api_view, name='notifications-list'),
        url(r'^api/', include(api_router.urls)),

        # Error logging testing
        url(r'^generate-500$', generate_exception_view),
    ) +
    vision_patterns() +
    patterns(
        '',
        url(r'^',                                   home_app_view,         name='app-home'),
    )
)
