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
    author_details = UserSerializer(source='author', read_only=True)

    class Meta:
        model = Vision
