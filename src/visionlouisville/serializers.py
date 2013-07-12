from rest_framework.serializers import (
    IntegerField, ModelSerializer,
    SerializerMethodField, RelatedField)
from .models import User, Vision, Reply, Moment
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
class UserSerializer (ManyToNativeMixin, ModelSerializer):
    avatar_url = SerializerMethodField('get_avatar_url')
    full_name = SerializerMethodField('get_full_name')
    groups = RelatedField(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar_url',
                  'full_name', 'groups')

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

    def many_to_native(self, many_obj):
        service = self.get_twitter_service()
        on_behalf_of = self.get_requesting_user()

        # Hit the service so that all the users' info is cached.
        service.get_users_info(many_obj, on_behalf_of)
        
        return super(UserSerializer, self).many_to_native(many_obj)


class MinimalUserSerializer (ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ReplySerializer (ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    tweet_id = IntegerField(read_only=True)

    class Meta:
        model = Reply


class MomentSerializer (ModelSerializer):
    id = SerializerMethodField('get_id')

    class Meta:
        model = Moment

    def get_id(self, obj):
        return 'moment-%s' % (obj.id,)


class VisionSerializer (ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    supporters = UserSerializer(many=True, read_only=True)
    sharers = MinimalUserSerializer(many=True, read_only=True)
    tweet_id = IntegerField(read_only=True)

    class Meta:
        model = Vision


class MomentSerializerWithType (MomentSerializer):
    type = SerializerMethodField('get_input_type')

    def get_input_type(self, obj):
        return 'moment'


class VisionSerializerWithType (VisionSerializer):
    type = SerializerMethodField('get_input_type')

    def get_input_type(self, obj):
        return 'vision'
