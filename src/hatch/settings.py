# Django settings for hatch project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

APP_CONFIG_CACHE_KEY = 'app_config'
APP_CONFIG_INDEX = 0

###############################################################################
#
# Time Zones
#

TIME_ZONE = 'US/Eastern'
USE_TZ = True

###############################################################################
#
# Internationalization and Localization
#

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

SITE_ID = 1

###############################################################################
#
# Templates and Static Assets
#

MEDIA_ROOT = ''
MEDIA_URL = ''

STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = ()

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = ()

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",

    "utils.context_processors.settings",
)

###############################################################################
#
# Server Configuration
#

WSGI_APPLICATION = 'hatch.wsgi.application'
ROOT_URLCONF = 'hatch.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social_auth.middleware.SocialAuthExceptionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'hatch.middleware.HatchAuthMiddleware',
)

SECRET_KEY = 'Set me in local settings!!!'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

###############################################################################
#
# Authentication
#

AUTH_USER_MODEL = 'hatch.User'

AUTHENTICATION_BACKENDS = (
    # See http://django-social-auth.readthedocs.org/en/latest/configuration.html
    # for list of available backends.
    'social_auth.backends.twitter.TwitterBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/'

###############################################################################
#
# 3rd-party service configuration and keys
#

TWITTER_CONSUMER_KEY         = ''  # Set me in local settings
TWITTER_CONSUMER_SECRET      = ''  # Set me in local settings

###############################################################################
#
# URL Shortening
#

SHORTEN_MODELS = {
    # 'm': 'meetingmatters.meetings.meeting',
}
#SHORT_BASE_URL = 'http://mtm.tt/'

###############################################################################
#
# Pluggable Applications
#

COMMUNITY_APPS = (
    'south',
    'django_nose',
    'debug_toolbar',
    'social_auth',
    'shorturls',
    'storages',
    'rest_framework',
    'jstemplate',
    'djcelery',
)

PROJECT_SPECIFIC_APPS = (
    'visionlouisville',
    'hatch',
    'utils',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments',
) + PROJECT_SPECIFIC_APPS + COMMUNITY_APPS


################################################################################
#
# Asynchronous tasks and processing
#

import djcelery
djcelery.setup_loader()

################################################################################
#
# Testing and administration
#

# Tests (nose)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
SOUTH_TESTS_MIGRATE = True

# Debug toolbar
def custom_show_toolbar(request):
    return SHOW_DEBUG_TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'INTERCEPT_REDIRECTS': False
}
INTERNAL_IPS = ('127.0.0.1',)


################################################################################
#
# Logging Configuration
#

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


###############################################################################
# Local settings overrides
try:
    from local_settings import *
except ImportError:
    pass

try:
    # Check whether the celery broker is the Django DB
    if BROKER_URL == 'django://':
        INSTALLED_APPS += ('kombu.transport.django',)
except NameError:
    pass