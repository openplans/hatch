import sys

from django.conf import settings as django_settings
from django.contrib.sites.models import Site

def settings(request):
		return {'settings': django_settings}

def site(request):
		return {'site': Site.objects.get_current()}
