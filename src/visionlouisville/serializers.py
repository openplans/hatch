from rest_framework.serializers import (
    IntegerField, ModelSerializer, PrimaryKeyRelatedField, 
    SerializerMethodField, URLField)
from .models import User, Vision, Reply
from .services import SocialMediaException


class UserSerializer (ModelSerializer):
    avatar_url = SerializerMethodField('get_avatar_url')
    full_name = SerializerMethodField('get_full_name')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar_url',
                  'full_name')

    def get_twitter_service(self):
        return self.context['twitter_service']

    def get_requesting_user(self):
        return self.context['requesting_user']

    def get_avatar_url(self, obj):
        service = self.get_twitter_service()
        on_behalf_of = self.get_requesting_user()
        try:
            return service.get_avatar_url(obj, on_behalf_of)
        except SocialMediaException:
            return None

    def get_full_name(self, obj):
        service = self.get_twitter_service()
        on_behalf_of = self.get_requesting_user()
        try:
            return service.get_full_name(obj, on_behalf_of)
        except SocialMediaException:
            return None


class ReplySerializer (ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    tweet_id = IntegerField(read_only=True)

    class Meta:
        model = Reply


class VisionSerializer (ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    supporters = UserSerializer(many=True, read_only=True)
    tweet_id = IntegerField(read_only=True)

    class Meta:
        model = Vision
