import os
import datetime

# Make filepaths relative to settings.
def rel_path(*subs):
    """Make filepaths relative to this settings file"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_path, *subs)

# Debug is False by default, true if set in the environment.
DEBUG = (os.environ.get('DEBUG', 'False') in ['true', 'True'])
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = DEBUG

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    rel_path('../static'),
)

SECRET_KEY = 'changemeloremipsumdolorsitametconsecteturadipisicingelit'
ALLOWED_HOSTS = ['*']

ADMINS = [
    (admin.split('@')[0], admin)
    for admin in os.environ.get('ADMINS', '').split(',')
]

EMAIL_SUBJECT_PREFIX = '[hatch] '

import dj_database_url
DATABASES = {'default': dj_database_url.config()}

import django_cache_url
CACHE = {'default': django_cache_url.config()}

# Image storing
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_QUERYSTRING_AUTH = False

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"

GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', "', ''); alert('Set your Google Analytics ID and domain!'); (function(){})('")
GOOGLE_ANALYTICS_DOMAIN = os.environ.get('GOOGLE_ANALYTICS_DOMAIN', 'dotcloud.com')

## ===========================================================================

# For sitemaps and caching -- will be a new value every time the server starts
LAST_DEPLOY_DATE = datetime.datetime.now().isoformat()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s\n%(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'hatch': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
