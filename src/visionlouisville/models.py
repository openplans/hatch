from django.conf import settings
from django.db import models
from django.db.models import query
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager

import logging
logger = logging.getLogger(__name__)


BaseUser = get_user_model()


class User (BaseUser):
    class Meta:
        proxy = True

    def support(self, vision):
        vision.supporters.add(self)

    def unsupport(self, vision):
        vision.supporters.remove(self)


class Vision (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, related_name='visions')
    category = models.CharField(max_length=20)
    title = models.CharField(max_length=160)
    description = models.TextField()
    supporters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='supporters')

    tweet_id = models.CharField(max_length=64, null=True)

    def __unicode__(self):
        return self.title


class Reply (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vision = models.ForeignKey(Vision, related_name='replies')
    author = models.ForeignKey(User, related_name='replies')
    text = models.CharField(max_length=140)

    tweet_id = models.CharField(max_length=64, null=True)

    class Meta:
        verbose_name_plural = 'replies'
