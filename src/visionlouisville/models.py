from django.db import models
from django.db.models import query
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager
from urlparse import parse_qs

import logging
logger = logging.getLogger(__name__)


class DataException (Exception):
    pass


BaseUser = get_user_model()
class User (BaseUser):
    class Meta:
        proxy = True

    def get_cache_key_prefix(self):
        return 'user-%s' % self.pk

    def get_cache_key(self, extra):
        return ':'.join([self.get_cache_key_prefix(), extra])

    @property
    def info(self):
        cache_key = self.get_cache_key('info')
        info = cache.get(cache_key)

        if info is None:
            if self.social_auth.provider == 'twitter':
                extra_data = self.social_auth.extra_data
                access_token = parse_qs(extra_data['access_token'])

                t = Twitter(auth=OAuth(
                    access_token['oauth_token'],
                    access_token['oauth_token_secret'],
                    settings.TWITTER_CONSUMER_KEY,
                    settings.TWITTER_CONSUMER_SECRET
                ))

                info = t.users.show(user_id=extra_data['id'])
                cache.set(cache_key, info)
            else:
                raise DataException(
                    ('Can\'t get info for a user authenticated with a %r '
                     'provider') % self.social_auth.provider
                )
        return info

    @property
    def avatar_url(self):
        if self.social_auth.provider == 'twitter':
            return self.info['profile_image_url']
        else:
            raise DataException(
                ('Can\'t get avatar URL for a user authenticated with a %r '
                 'provider') % self.social_auth.provider
            )


class Vision (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=160)
    category = models.CharField(max_length=20)

    def __unicode__(self):
        return self.content
