from django.db import models
from django.db.models import query
from django.utils.translation import ugettext as _
from django.utils.timezone import now

import logging
logger = logging.getLogger(__name__)


class Vision (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=160)
    category = models.CharField(max_length=20)

    def __unicode__(self):
        return self.content
