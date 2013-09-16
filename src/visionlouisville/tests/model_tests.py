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


class TweetTest (TestCase):
    def tearDown(self):
        User.objects.all().delete()
        Vision.objects.all().delete()
        Tweet.objects.all().delete()
        cache.clear()

    def test_converting_to_simple_vision(self):
        tweet = Tweet.objects.create(tweet_id='abc123', tweet_data={
            'user': {
                'id': '123456',
                'screen_name': 'tweeter',
                'name': 'A. User',
            },
            'text': 'this is a tweet',
            'entities': {},
        })
        vision = tweet.make_vision()

        assert_equal(vision.tweet_id, 'abc123')
        assert_equal(vision.author.username, 'tweeter')
        assert_equal(vision.text, 'this is a tweet')
        assert_equal(vision.category, None)

    def test_converting_to_vision_with_media(self):
        tweet = Tweet.objects.create(tweet_id='abc123', tweet_data={
            'user': {
                'id': '123456',
                'screen_name': 'tweeter',
                'name': 'A. User',
            },
            'text': 'this is a tweet',
            'entities': {
                'media': [
                    {
                        'type': 'movie',  # Not a photo type
                        'media_url': 'http://example.com/movie.mp4'
                    },
                    {
                        'type': 'photo',
                        'media_url': 'http://example.com/picture.png'
                    },
                    {
                        'type': 'photo',  # Only use the first photo
                        'media_url': 'http://fakin.it/nopic.txt'
                    }
                ]
            }
        })
        vision = tweet.make_vision()

        assert_equal(vision.media_url, 'http://example.com/picture.png')

    def test_converting_to_visions_with_same_user(self):
        tweet1 = Tweet.objects.create(tweet_id='abc123', tweet_data={
            'user': {
                'id': '123456',
                'screen_name': 'tweeter',
                'name': 'A. User',
            },
            'text': 'this is a tweet',
            'entities': {},
        })
        vision1 = tweet1.make_vision()

        tweet2 = Tweet.objects.create(tweet_id='abc124', tweet_data={
            'user': {
                'id': '123456',
                'screen_name': 'tweeter',
                'name': 'A. User',
            },
            'text': 'this is a tweet',
            'entities': {}
        })
        vision2 = tweet2.make_vision()

        assert_equal(vision1.author.username, 'tweeter')
        assert_equal(vision2.author.id, vision1.author.id)

    @patch.object(Vision, 'save')
    def test_converting_to_vision_without_commit(self, save):
        tweet = Tweet.objects.create(tweet_id='abc123', tweet_data={
            'user': {
                'id': '123456',
                'screen_name': 'tweeter',
                'name': 'A. User',
            },
            'text': 'this is a tweet',
            'entities': {},
        })
        vision = tweet.make_vision(commit=False)

        assert_equal(vision.pk, None)
        assert_equal(save.call_count, 0)

    def test_converting_many_to_visions(self):
        Tweet.objects.create(tweet_id='abc123', tweet_data={
            'user': {
                'id': '123456',
                'screen_name': 'tweeter',
                'name': 'A. User',
            },
            'text': 'this is a tweet',
            'entities': {},
        })
        Tweet.objects.create(tweet_id='abc124', tweet_data={
            'user': {
                'id': '123456',
                'screen_name': 'tweeter',
                'name': 'A. User',
            },
            'text': 'this is a tweet',
            'entities': {},
        })

        visions = Tweet.objects.all().make_visions()
        assert_equal(len(visions), 2)
        assert_equal(visions[0].author.id, visions[1].author.id)
