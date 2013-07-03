from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user as base_get_user
from .models import User


def get_user(request):
    base_user = base_get_user(request)
    if base_user.is_authenticated():
        user = User()
        user.__dict__ = base_user.__dict__
        return user
    else:
        return base_user


class VisionLouisvilleAuthMiddleware(object):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
