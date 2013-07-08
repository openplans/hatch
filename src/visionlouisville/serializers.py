from rest_framework.serializers import ModelSerializer, SerializerMethodField, URLField
from .models import User, Vision
from .services import SocialMediaException


class UserSerializer (ModelSerializer):
    avatar_url = SerializerMethodField('get_avatar_url')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar_url')

    def get_avatar_url(self, obj):
        twitter_service = self.context['twitter_service']
        try:
            return twitter_service.get_avatar_url(obj)
        except SocialMediaException:
            return None


class VisionSerializer (ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)

    class Meta:
        model = Vision
