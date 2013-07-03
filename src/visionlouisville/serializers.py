from rest_framework.serializers import ModelSerializer, URLField
from .models import User, Vision


class UserSerializer (ModelSerializer):
    avatar_url = URLField()

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar_url')


class VisionSerializer (ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Vision
