from rest_framework.serializers import ModelSerializer, SerializerMethodField, URLField
from .models import User, Vision


class UserSerializer (ModelSerializer):
    avatar_url = SerializerMethodField('get_avatar_url')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar_url')

    def get_avatar_url(self, obj):
        return obj.avatar_url


class VisionSerializer (ModelSerializer):
    author_avatar_url = SerializerMethodField('get_avatar_url')

    class Meta:
        model = Vision

    def get_avatar_url(self, obj):
        return obj.author.avatar_url
        # twitter_service = self.context['twitter_service']
        # return twitter_service.get_avatar_url(obj.author_pk)
