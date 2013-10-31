from rest_framework.serializers import (
    CharField, ImageField, IntegerField, ModelSerializer,
    PrimaryKeyRelatedField, SerializerMethodField, DateTimeField,
    RelatedField, ValidationError)
from .models import User, Vision, Reply, Category, AppConfig
from .services import SocialMediaException


# ============================================================
# This is a DRF-related patch, pending either a better way to
# do this, or acceptance and integration of the DRF issue
# https://github.com/tomchristie/django-rest-framework/pull/982
# ============================================================
class ManyToNativeMixin (object):
    def many_to_native(self, value):
        return [self.to_native(item) for item in value]

    def field_to_native(self, obj, field_name):
        """
        Override default so that the serializer can be used as a nested field
        across relationships.
        """
        from rest_framework.serializers import ObjectDoesNotExist, get_component, is_simple_callable

        if self.source == '*':
            return self.to_native(obj)

        try:
            source = self.source or field_name
            value = obj

            for component in source.split('.'):
                value = get_component(value, component)
                if value is None:
                    break
        except ObjectDoesNotExist:
            return None

        if is_simple_callable(getattr(value, 'all', None)):
            return self.many_to_native(value.all())

        if value is None:
            return None

        if self.many is not None:
            many = self.many
        else:
            many = hasattr(value, '__iter__') and not isinstance(value, (Page, dict, six.text_type))

        if many:
            return self.many_to_native(value)
        return self.to_native(value)

    @property
    def data(self):
        """
        Returns the serialized data on the serializer.
        """
        from rest_framework.serializers import warnings

        if self._data is None:
            obj = self.object

            if self.many is not None:
                many = self.many
            else:
                many = hasattr(obj, '__iter__') and not isinstance(obj, (Page, dict))
                if many:
                    warnings.warn('Implict list/queryset serialization is deprecated. '
                                  'Use the `many=True` flag when instantiating the serializer.',
                                  DeprecationWarning, stacklevel=2)

            if many:
                self._data = self.many_to_native(obj)
            else:
                self._data = self.to_native(obj)

        return self._data


# ============================================================
# The serializers
# ============================================================
class BaseTwitterInfoSerializer (ModelSerializer):
    avatar_url = SerializerMethodField('get_avatar_url')
    full_name = SerializerMethodField('get_full_name')
    bio = SerializerMethodField('get_bio')

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

    def get_bio(self, obj):
        service = self.get_twitter_service()
        on_behalf_of = self.get_requesting_user()
        try:
            return service.get_bio(obj, on_behalf_of)
        except SocialMediaException:
            return None

    def many_to_native(self, many_obj):
        service = self.get_twitter_service()
        on_behalf_of = self.get_requesting_user()

        # Hit the service so that all the users' info is cached.
        service.get_users_info(many_obj, on_behalf_of)

        return super(UserSerializer, self).many_to_native(many_obj)


class MinimalTwitterUserSerializer (BaseTwitterInfoSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar_url', 'full_name', 'bio')


class MinimalUserSerializer (ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class MinimalVisionSerializer (ModelSerializer):
    author_details = MinimalTwitterUserSerializer(source='author', read_only=True)

    class Meta:
        model = Vision
        fields = ('id', 'created_at', 'category', 'text', 'supporters', 'author_details')


class MinimalReplySerializer (ModelSerializer):
    vision = MinimalVisionSerializer(source='vision', read_only=True)

    class Meta:
        model = Reply
        fields = ('id', 'text', 'vision')


class UserSerializer (ManyToNativeMixin, BaseTwitterInfoSerializer):
    replies = MinimalReplySerializer(many=True, read_only=True)
    visions = MinimalVisionSerializer(many=True, read_only=True)
    supported = MinimalVisionSerializer(many=True, read_only=True)
    groups = RelatedField(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar_url',
                  'full_name', 'bio', 'groups', 'last_login', 'supported',
                  'replies', 'visions')


class ReplySerializer (ModelSerializer):
    author_details = MinimalTwitterUserSerializer(source='author', read_only=True)
    tweet_id = IntegerField(read_only=True)

    class Meta:
        model = Reply
        exclude = ('tweet',)


class CategorySerializer (ModelSerializer):
    class Meta:
        model = Category


class AppConfigSerializer (ModelSerializer):
    class Meta:
        model = AppConfig


class VisionSerializer (ModelSerializer):
    author_details = MinimalTwitterUserSerializer(source='author', read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    supporters = MinimalUserSerializer(many=True, read_only=True)
    sharers = PrimaryKeyRelatedField(many=True, read_only=True)
    tweet_id = IntegerField(read_only=True)
    category = PrimaryKeyRelatedField(required=False)
    created_at = DateTimeField(required=False)
    updated_at = DateTimeField(required=False)

    class Meta:
        model = Vision
        exclude = ('tweet',)

    def from_native(self, data, files):
        # Validate any uploaded media
        media_field = ImageField(required=False)
        media_file = files.get('media', None)
        try:
            media = media_field.from_native(media_file)
        except ValidationError as err:
            if not hasattr(self, '_errors') or self._errors is None:
                self._errors = {}
            self._errors['media'] = list(err.messages)
            return

        # Attach uploaded media, if appropriate
        if media and 'media_url' not in data:
            data['media_url'] = Vision.upload_photo(media)

        return super(VisionSerializer, self).from_native(data, {})
