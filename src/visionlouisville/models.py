from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models, IntegrityError, transaction
from django.db.models import query
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group, AbstractUser
from jsonfield import JSONField
from random import randint
from social_auth.models import UserSocialAuth
from os.path import join as path_join
from uuid import uuid1, uuid4
import json
import re

import logging
logger = logging.getLogger(__name__)


class User (AbstractUser):
    visible_on_home = models.BooleanField(default=True)

    def support(self, vision):
        vision.supporters.add(self)

    def unsupport(self, vision):
        vision.supporters.remove(self)

    def share(self, vision, share_id=None):
        self.support(vision)
        share = Share(vision=vision, user=self, tweet_id=share_id)
        share.save()
        return share

    def unshare(self, vision):
        self.unsupport(vision)
        share = Share.objects.get(user=self, vision=vision)
        share.delete()

    def add_to_group(self, group_name):
        group = Group.objects.get(name=group_name)
        self.groups.add(group)

    def remove_from_group(self, group_name):
        group = Group.objects.get(name=group_name)
        self.groups.remove(group)


class TweetQuerySet (query.QuerySet):
    def make_visions(self):
        visions = []
        for tweet in self.all():
            visions.append(tweet.make_vision(commit=False))
        Vision.objects.bulk_create(visions)
        return visions


def get_tweet_id(tweet_data):
    try:
        if isinstance(tweet_data, (int, str, unicode)):
            return int(tweet_data)
        else:
            return tweet_data['id']

    except (ValueError, TypeError, KeyError):
        raise ValueError(
            'Expected the numeric id of a tweet, or a dictionary-like '
            'object representing a tweet: %r'
            % tweet_data)


class TweetManager (models.Manager):
    def create_or_update_from_tweet_data(self, tweet_data):
        tweet_id = get_tweet_id(tweet_data)

        qs = self.get_query_set()
        ModelClass = self.model

        try:
            obj = qs.get(tweet_id=tweet_id)
            created = False
        except ModelClass.DoesNotExist:
            obj = ModelClass()
            created = True

        try:
            # TODO: Change to transaction.atomic when upgrading to Django 1.6
            with transaction.commit_on_success():
                obj.load_from_tweet_data(tweet_data)
        except IntegrityError:
            # Since we've already checked for objects with this tweet_id, we would
            # only have an integrity error at this point if some other thread or
            # process created a object with the same tweet ID right before the
            # obj.save(). Since that's the case, just assume that we're ok with
            # that.
            pass

        return obj, created


class TweetedObjectManager (models.Manager):
    """
    Using this manager requires the associated model to:
      * Have a tweet_id attribute, and
      * Have a load_from_tweet method that takes either a tweet id or a
        dictionary that represents tweet
    """
    def create_or_update_from_tweet_data(self, tweet_data):
        tweet = Tweet.objects.create_or_update_from_tweet_data(tweet_data)

        qs = self.get_query_set()
        ModelClass = self.model

        try:
            obj = qs.get(tweet=tweet)
            created = False
        except ModelClass.DoesNotExist:
            obj = ModelClass()
            created = True

        try:
            # TODO: Change to transaction.atomic when upgrading to Django 1.6
            with transaction.commit_on_success():
                obj.sync_with_tweet(tweet)
        except IntegrityError:
            # Since we've already checked for objects with this tweet_id, we would
            # only have an integrity error at this point if some other thread or
            # process created a object with the same tweet ID right before the
            # obj.save(). Since that's the case, just assume that we're ok with
            # that.
            pass

        return obj, created


class Tweet (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tweet_id = models.CharField(
        max_length=64, primary_key=True,
        help_text=(_(
            "You can fill in the tweet id and leave the text field blank (you "
            "must select an author, though it will be updated to be the tweet "
            "creator). For example, if the tweet URL is http://www.twitter.com"
            "/myuser/status/1234567890, then the tweet id is 1234567890.")))
    tweet_data = JSONField(blank=True, default={})

    objects = TweetManager()

    def __unicode__(self):
        return self.tweet_id

    @classmethod
    def get_tweet_data(cls, tweet_id):
        """
        Take either a tweet id or a tweet dictionary and normalize into a
        tweet dictionary.
        """
        tweet_url_pattern = r'https?://(?:www\.)?twitter.com/[A-Za-z0-9-_]+/status/(?P<tweet_id>\d+)'

        if isinstance(tweet_id, (str, unicode)):
            match = re.match(tweet_url_pattern, tweet_id)
            if match:
                tweet_id = match.group('tweet_id')

        if isinstance(tweet_id, (int, str, unicode)):
            from services import default_twitter_service as twitter_service
            t = twitter_service.get_api()
            tweet_data = t.statuses.show(id=tweet_id)
        else:
            tweet_data = tweet_id
        return tweet_data

    def make_vision(self, commit=True):
        vision = Vision(tweet=self)
        vision.sync_with_tweet(self, commit=commit)
        return vision

    def load_from_tweet_data(self, tweet_id, commit=True):
        tweet_data = self.get_tweet_data(tweet_id)
        self.tweet_id = tweet_data['id']
        self.tweet_data = tweet_data

        if commit:
            self.save()

    def save(self, *args, **kwargs):
        if self.tweet_id and not self.tweet_data:
            self.load_from_tweet_data(self.tweet_id, commit=False)
        return super(Tweet, self).save(*args, **kwargs)


class TweetedModelMixin (object):
    @classmethod
    def get_or_create_tweeter(cls, user_info):
        user_id = user_info['id']
        username = user_info['screen_name']
        try:
            user_social_auth = UserSocialAuth.objects.get(uid=user_id, provider='twitter')
            user = user_social_auth.user
        except UserSocialAuth.DoesNotExist:
            suffix = ''
            while True:
                user, created = User.objects.get_or_create(username=username + suffix)
                if created:
                    user_full_name = user_info['name'].split(' ', 1)
                    user.first_name = user_full_name[0]
                    if len(user_full_name) > 1:
                        user.last_name = user_full_name[1]
                    user.save()

                    extra_data = user_info.copy()
                    extra_data['access_token'] = 'oauth_token_secret=123&oauth_token=abc'

                    user_social_auth = UserSocialAuth.objects.create(
                        user=user,
                        uid=user_id,
                        provider='twitter',
                        extra_data=json.dumps(extra_data),
                    )

                    break
                else:
                    suffix = str(uuid1())
        return user

    def set_media_from_tweet(self, tweet):
        for media in tweet.tweet_data['entities'].get('media', []):
            if media['type'] == 'photo':
                self.media_url = media['media_url']
                break

    def set_text_from_tweet(self, tweet):
        self.text = tweet.tweet_data['text']

    def set_user_from_tweet(self, tweet):
        user = self.get_or_create_tweeter(tweet.tweet_data['user'])
        self.author = user


class Category (models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=100)
    prompt = models.TextField()

    def __unicode__(self):
        return unicode(self.name)


class Vision (TweetedModelMixin, models.Model):
    tweet = models.OneToOneField('Tweet', related_name='vision', null=True)
    author = models.ForeignKey(User, related_name='visions')
    category = models.ForeignKey(Category, related_name='visions', null=True, blank=True)
    text = models.TextField(blank=True)
    media_url = models.URLField(default='', blank=True)
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(blank=True)
    updated_at = models.DateTimeField(blank=True)

    supporters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='supported', blank=True)
    sharers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='sharers', blank=True, through='Share')

    objects = TweetedObjectManager()

    class Meta:
        ordering = ('-created_at',)

    def __unicode__(self):
        return self.text[:140]

    @classmethod
    def get_photo_path(cls, filename):
        if '.' in filename:
            ext = filename.split('.')[-1]
            filename = "%s.%s" % (uuid4(), ext)
        else:
            filename = str(uuid4())
        return path_join('photos', now().strftime('%Y/%m/%d'), filename)

    @classmethod
    def upload_photo(cls, photo, storage=default_storage):
        path = cls.get_photo_path(photo.name)
        with storage.open(path, 'wb+') as destination:
            for chunk in photo.chunks():
                destination.write(chunk)
        return storage.url(path)

    def attach_photo(self, photo, storage=default_storage):
        self.media_url = self.upload_photo(photo, storage)

    def sync_with_tweet(self, tweet, commit=True):
        self.set_text_from_tweet(tweet)
        self.set_user_from_tweet(tweet)
        self.set_media_from_tweet(tweet)

        if commit:
            self.save()

    def save(self, *args, **kwargs):
        # Manually set the created/updated at
        if not self.id:
            self.created_at = now()
        self.updated_at = now()

        if self.tweet and not any([self.text, self.media_url]):
            self.sync_with_tweet(self.tweet, commit=False)
        return super(Vision, self).save(*args, **kwargs)


class Share (models.Model):
    vision = models.ForeignKey(Vision)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='shares')
    tweet = models.ForeignKey('Tweet', related_name='shares')

    def __unicode__(self):
        return '%s shared "%s"' % (self.user, self.vision)


class Reply (TweetedModelMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tweet = models.OneToOneField('Tweet', related_name='reply')
    vision = models.ForeignKey(Vision, related_name='replies')
    author = models.ForeignKey(User, related_name='replies')
    text = models.CharField(max_length=140, blank=True)

    objects = TweetedObjectManager()

    class Meta:
        verbose_name_plural = 'replies'
        ordering = ('created_at',)

    def __unicode__(self):
        return '%s replied to "%s"' % (self.author, self.vision)

    def sync_with_tweet(self, tweet, commit=True):
        self.set_text_from_tweet(tweet)
        self.set_user_from_tweet(tweet)

        if commit:
            self.save()

    def save(self, *args, **kwargs):
        if self.tweet and not any([self.text]):
            self.sync_with_tweet(self.tweet, commit=False)
        return super(Reply, self).save(*args, **kwargs)
