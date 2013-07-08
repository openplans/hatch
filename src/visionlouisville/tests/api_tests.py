from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from ..services import TwitterService
from ..serializers import VisionSerializer, UserSerializer
from ..views import VisionViewSet, UserViewSet
from ..models import Vision, User
from social_auth.models import UserSocialAuth
from mock import patch
import json


class VisionsTest (TestCase):
    def test_vision_contents(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        vision = Vision.objects.create(author=user, title='my vision')
        factory = RequestFactory()
        params = {'pk': vision.pk}
        url = reverse('vision-detail', kwargs=params)

        view = VisionViewSet.as_view({'get': 'retrieve'})

        request = factory.get(url)
        response = view(request, **params)
        response.render()

        data = json.loads(response.content)
        self.assertIn('author_details', data)
        self.assertEqual(data['author_details'].get('username'), user.username)
        self.assertEqual(data.get('id'), vision.pk)
        self.assertEqual(data.get('title'), vision.title)
        self.assertEqual(data.get('description'), vision.description)


class UserSerializerTest (TestCase):
    def test_non_twitter_user(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        serializer = UserSerializer(user)
        serializer.context['twitter_service'] = TwitterService()
        serializer.context['requesting_user'] = None

        data = serializer.data
        self.assertIn('avatar_url', data)
        self.assertIsNone(data.get('avatar_url'))

    def test_user_contents(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        social_auth = UserSocialAuth.objects.create(user=user, provider='twitter', extra_data='{"access_token": "oauth_token_secret=abc&oauth_token=123", "id": 42}')
        serializer = UserSerializer(user)
        serializer.context['twitter_service'] = TwitterService()
        serializer.context['requesting_user'] = None

        def get_stub_api(self, user=None):
            class StubTwitter (object):
                class users:
                    @staticmethod
                    def show(user_id):
                        return {
                            'name': 'Mjumbe Poe', 
                            'profile_image_url': 'http://www.google.com/happy_ducks.png'
                        }
            return StubTwitter()

        with patch('visionlouisville.services.TwitterService.get_api', get_stub_api):
            data = serializer.data
            self.assertEqual(data.get('avatar_url'), 'http://www.google.com/happy_ducks.png')
            self.assertEqual(data.get('full_name'), 'Mjumbe Poe')
