from django.test import TestCase, RequestFactory
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from ..services import TwitterService
from ..models import Vision, User, Reply, Tweet
from social_auth.models import UserSocialAuth
from mock import patch, Mock
from nose.tools import assert_equal
import json


class FollowedUserTest (TestCase):
    def tearDown(self):
        User.objects.all().delete()
        cache.clear()

    def test_gets_ids_of_followed_users(self):
        friends_twitter_response = {
          "ids": [
            1335646238,
            735844561,
            398803785,
            188834632,
            20846384,
            143754070,
            1020576846,
            9926872,
            1578228931,
            236419493
          ],
          "next_cursor": 0,
          "next_cursor_str": "0",
          "previous_cursor": 0,
          "previous_cursor_str": "0"
        }

        class StubTwitterAPI (object):
            @property
            def friends(self):
                class Stub (object):
                    def ids(self, user_id):
                        return friends_twitter_response
                return Stub()

        service = TwitterService()

        with patch.object(service, 'get_api') as get_twitter_api:
            get_twitter_api.return_value = StubTwitterAPI()

            user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
            social_auth = UserSocialAuth.objects.create(user=user, uid=42, provider='twitter', extra_data='{"access_token": "oauth_token_secret=abc&oauth_token=123", "id": 42}')
            user_ids = service.get_followed_users(user, user)

            self.assertEqual(len(user_ids), 10)
