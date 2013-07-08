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


class Vision (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, related_name='visions')
    category = models.CharField(max_length=20)
    title = models.CharField(max_length=160)
    description = models.TextField()

    def get_user_tweet_text(self, request):
        vision_url = request.build_absolute_uri(
            '/#!/visions/%s' % self.pk)
            # reverse('vision-detail', kwargs={'pk': self.pk}))
        category = self.category.lower()
        username = self.author.username

        return \
            'Check out this vision about %s in Louisville, from @%s: %s' % (
                category, 
                username, 
                vision_url
            )

    def __unicode__(self):
        return self.title
