from django.test import TestCase, RequestFactory
from django.conf import settings
from django.core.urlresolvers import reverse, clear_url_caches
from django.core.cache import cache
from .utils import create_app_config
from ..services import TwitterService
from ..serializers import VisionSerializer, UserSerializer
from ..views import VisionViewSet, UserViewSet, ReplyViewSet, VisionActionViewSet
from ..models import Vision, User, Reply, Category, Tweet, AppConfig, Share
from ..cache import cache_buffer
from social_auth.models import UserSocialAuth
from mock import patch, Mock
import json


class VisionsTest (TestCase):
    def setUp(self):
        create_app_config()
        cache.clear()
        cache_buffer.reset()

        # Reload the urls to reinitialize the vision routes
        import hatch.urls
        reload(hatch.urls)
        clear_url_caches()

    def tearDown(self):
        User.objects.all().delete()
        Vision.objects.all().delete()
        AppConfig.objects.all().delete()
        cache.clear()
        cache_buffer.reset()

    def test_vision_contents(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        category = Category.objects.create(name='a', title='b', prompt='c')
        vision = Vision.objects.create(author=user, text='my vision', category_id=category.pk)
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
        self.assertEqual(data.get('text'), vision.text)

    def test_vision_app_tweeting(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        category = Category.objects.create(name='economy', title='', prompt='')
        factory = RequestFactory()
        url = reverse('vision-list')

        class StubTwitterService (object):
            tweet = Mock(return_value=(True, {'id': 12345, 'user': {'id_str': '2468', 'screen_name': 'bobs_burgers'}}))

            def get_avatar_url(self, user, actor=None):
                return ''

            def get_full_name(self, user, actor=None):
                return ''

            def get_bio(self, user, actor=None):
                return ''

            def get_users_info(self, users, actor=None):
                return []

            def get_url_length(self, url, actor=None):
                return 20

        with patch('hatch.views.VisionViewSet.get_twitter_service', classmethod(lambda cls: StubTwitterService())):
            view = VisionViewSet.as_view({'post': 'create'})
            request = factory.post(url, data=json.dumps({
                    'author': user.pk,
                    'category': 'economy',
                    'text': 'This is a vision -- More information about the vision'
                }), content_type='application/json')
            request.user = user
            request.csrf_processing_done = True

            response = view(request)
            response.render()

            self.assertEqual(StubTwitterService.tweet.call_count, 1, response.content)
            self.assertIn('@mjumbe', StubTwitterService.tweet.call_args[0][0])
            self.assertEqual(len(StubTwitterService.tweet.call_args[0]), 1)

    def test_vision_user_tweeting(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        category = Category.objects.create(name='economy', title='', prompt='')
        factory = RequestFactory()
        url = reverse('vision-list')

        class StubTwitterService (object):
            tweet = Mock(return_value=(True, {'id': 12345, 'user': {'id_str': '2468', 'screen_name': 'bobs_burgers'}}))

            def get_avatar_url(self, user, actor=None):
                return ''

            def get_full_name(self, user, actor=None):
                return ''

            def get_bio(self, user, actor=None):
                return ''

            def get_url_length(self, url, actor=None):
                return 20

            def get_users_info(self, users, actor=None):
                return []

        with patch('hatch.views.VisionViewSet.get_twitter_service', classmethod(lambda cls: StubTwitterService())):
            view = VisionViewSet.as_view({'post': 'create'})
            vision_data = {
                'author': user.pk,
                'category': 'economy',
                'text': 'This is a vision'
            }
            request = factory.post(url, data=json.dumps(vision_data), 
                content_type='application/json',
                HTTP_X_SEND_TO_TWITTER='on')
            request.user = user
            request.csrf_processing_done = True

            response = view(request)
            response.render()

            self.assertEqual(StubTwitterService.tweet.call_count, 2)
            self.assert_(StubTwitterService.tweet.call_args_list[1][0][0].startswith(vision_data['text']), vision_data['text'])
            self.assertEqual(len(StubTwitterService.tweet.call_args_list[1][0]), 2)
            self.assertEqual(StubTwitterService.tweet.call_args_list[1][0][1], user)

    def test_handle_vision_app_tweeting_failure(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        factory = RequestFactory()
        url = reverse('vision-list')

        class StubTwitterService (object):
            tweet = Mock(return_value=(False, 'Something happened!'))

            def get_url_length(self, url, actor=None):
                return 20

        with patch('hatch.views.VisionViewSet.get_twitter_service', classmethod(lambda cls: StubTwitterService())):
            view = VisionViewSet.as_view({'post': 'create'})
            request = factory.post(url, data=json.dumps({
                    'author': user.pk,
                    'category': 'economy',
                    'text': 'This is a vision',
                }), content_type='application/json')
            request.user = user
            request.csrf_processing_done = True

            response = view(request)
            response.render()

            self.assertEqual(Vision.objects.all().count(), 0)
            self.assertEqual(response.status_code, 400)


class ReplyTest (TestCase):
    def setUp(self):
        create_app_config()

    def tearDown(self):
        User.objects.all().delete()
        Vision.objects.all().delete()
        Reply.objects.all().delete()
        cache.clear()

    def test_reply_tweeting(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        tweet = Tweet.objects.create(tweet_id='c', tweet_data={'text': 'abc'})
        vision = Vision.objects.create(author=user, text='abc', tweet_id='c')
        factory = RequestFactory()
        url = reverse('reply-list')

        class StubTwitterService (object):
            tweet = Mock(return_value=(True, {'id': 12345, 'user': {'id_str': '24680', 'screen_name': 'abc'}}))

            def get_avatar_url(self, user, actor=None):
                return ''

            def get_full_name(self, user, actor=None):
                return ''

            def get_bio(self, user, actor=None):
                return ''

            def get_url_length(self, url, actor=None):
                return 20

        with patch('hatch.views.ReplyViewSet.get_twitter_service', classmethod(lambda cls: StubTwitterService())):
            view = ReplyViewSet.as_view({'post': 'create'})
            request = factory.post(url, data=json.dumps({
                    'author': user.pk,
                    'vision': vision.pk,
                    'text': 'This is a reply',
                }), content_type='application/json')
            request.user = user
            request.csrf_processing_done = True

            response = view(request)
            response.render()

            self.assertEqual(StubTwitterService.tweet.call_count, 1, response.content)
            self.assertIn('in_reply_to_status_id', StubTwitterService.tweet.call_args[1])
            self.assertEqual(len(StubTwitterService.tweet.call_args[0]), 2)
            self.assertEqual(StubTwitterService.tweet.call_args[0][1], user)
            self.assertIn('@'+AppConfig.get().twitter_handle, StubTwitterService.tweet.call_args[0][0])

    def test_handle_reply_tweeting_failure(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        tweet = Tweet.objects.create(tweet_id='c', tweet_data={'text': 'abc'})
        vision = Vision.objects.create(author=user, text='abc', tweet=tweet)
        factory = RequestFactory()
        url = reverse('reply-list')

        class StubTwitterService (object):
            tweet = Mock(return_value=(False, 'Something happened!'))

        with patch('hatch.views.ReplyViewSet.get_twitter_service', classmethod(lambda cls: StubTwitterService())):
            view = ReplyViewSet.as_view({'post': 'create'})
            request = factory.post(url, data=json.dumps({
                    'author': user.pk,
                    'vision': vision.pk,
                    'text': 'This is a reply',
                }), content_type='application/json')
            request.user = user
            request.csrf_processing_done = True

            response = view(request)
            response.render()

            self.assertEqual(Reply.objects.all().count(), 0)
            self.assertEqual(response.status_code, 400)
            self.assertIn('tweet', response.content)


class ShareTest (TestCase):
    def setUp(self):
        create_app_config()

    def tearDown(self):
        User.objects.all().delete()
        Vision.objects.all().delete()
        Share.objects.all().delete()
        cache.clear()

    def test_share_retweeting(self):
        user = User.objects.create_user('mjumbe', 'mjumbe@example.com', 'password')
        tweet = Tweet.objects.create(tweet_id='c', tweet_data={'text': 'abc'})
        vision = Vision.objects.create(author=user, text='abc', tweet_id='c')
        factory = RequestFactory()
        url = reverse('support-vision-action', kwargs={'pk': vision.pk})

        class StubTwitterService (object):
            retweet = Mock(return_value=(True, {'id': 12345, 'user': {'id_str': '24680', 'screen_name': 'abc'}}))

            def get_avatar_url(self, user, actor=None):
                return ''

            def get_full_name(self, user, actor=None):
                return ''

            def get_bio(self, user, actor=None):
                return ''

            def get_url_length(self, url, actor=None):
                return 20

        with patch('hatch.views.VisionActionViewSet.get_twitter_service', classmethod(lambda cls: StubTwitterService())):
            view = VisionActionViewSet.as_view({'post': 'share'})
            request = factory.post(url, data='{}', content_type='application/json')
            request.user = user
            request.csrf_processing_done = True

            response = view(request, pk=vision.pk)
            response.render()

            self.assertEqual(StubTwitterService.retweet.call_count, 1, response.content)
            self.assertEqual(204, response.status_code)
            self.assertEqual(len(StubTwitterService.retweet.call_args[0]), 2)
            self.assertEqual(StubTwitterService.retweet.call_args[0][1], user)
            self.assertEqual(StubTwitterService.retweet.call_args[0][0], 'c')

            try:
                share = Share.objects.get(vision=vision, user=user)
            except Share.DoesNotExist:
                self.assert_(False, 'Share object not found')

            self.assertEqual(share.retweet_id, '12345')


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
        social_auth = UserSocialAuth.objects.create(user=user, uid=42, provider='twitter', extra_data='{"access_token": "oauth_token_secret=abc&oauth_token=123", "id": 42}')
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
                            'profile_image_url': 'http://www.google.com/happy_ducks.png',
                            'description': 'A stand-up guy'
                        }
            return StubTwitter()

        with patch('hatch.services.TwitterService.get_api', get_stub_api):
            data = serializer.data
            # Note that we're using the 'bigger' avatar variants.
            self.assertEqual(data.get('avatar_url'), 'http://www.google.com/happy_ducks_bigger.png')
            self.assertEqual(data.get('full_name'), 'Mjumbe Poe')
