from django.conf import settings
from django.core.cache import cache
from twitter import Twitter, OAuth, TwitterHTTPError
from twitter.stream import TwitterStream
from urlparse import parse_qs
import re
from .utils import chunk

from logging import getLogger
log = getLogger(__name__)


# ============================================================
# Exceptions
# ============================================================

class SocialMediaException (Exception):
    pass


# ============================================================
# The Twitter service
# ============================================================

class TwitterService (object):
    # ==================================================================
    # General Twitter info, cached
    # ==================================================================
    def get_config_cache_key(self):
        return 'twitter-config'

    def get_config(self, on_behalf_of=None):
        cache_key = self.get_config_cache_key()
        config = cache.get(cache_key)

        if config is None:
            t = self.get_api(on_behalf_of)
            config = t.help.configuration()
            config = dict(config.items())
            cache.set(cache_key, config)
        return config

    def get_url_length(self, url, on_behalf_of=None):
        config = self.get_config(on_behalf_of)
        if url.startswith('http://localhost') or url.startswith('http://127.0.0.1'):
            return len(url)

        if url.startswith('https'):
            return config['short_url_length_https']
        else:
            return config['short_url_length']

    # ==================================================================
    # User specific info, from Twitter, cached
    # ==================================================================
    def get_user_cache_key_prefix(self, user):
        return 'user-%s' % user.pk

    def get_user_cache_key(self, user, extra):
        return ':'.join([self.get_user_cache_key_prefix(user), extra])

    def get_user_info(self, user, on_behalf_of=None):
        cache_key = self.get_user_cache_key(user, 'info')
        info = cache.get(cache_key)

        if info is None:
            user_id = self.get_user_id(user)

            log_string = (
                '\n'
                '============================================================\n'
                'Hitting the API for %s to get info on %s (%s)\n'
                '============================================================\n'
            ) % (
                on_behalf_of.username if on_behalf_of else 'the app',
                user.username, user_id
            )
            log.info(log_string)

            t = self.get_api(on_behalf_of)
            info = t.users.show(user_id=user_id)
            info = dict(info.items())  # info is a WrappedTwitterResponse
            cache.set(cache_key, info)
        return info

    def get_users_info(self, users, on_behalf_of=None):
        # Build a mapping from cache_key => user_id
        data = {}
        for user in users:
            try:
                cache_key = self.get_user_cache_key(user, 'info')
                user_id = self.get_user_id(user)
                data[cache_key] = user_id
            except SocialMediaException as e:
                log.warning(e)
                pass

        # Build a reverse mapping from user_id => cache_key
        reverse_data = dict([
            (user_id, cache_key)
            for cache_key, user_id in data.items()
        ])

        # Get all the user info that is currently cached for the given users
        all_info = cache.get_many(data.keys())

        # Build a list of keys that have no cached data
        uncached_keys = filter(lambda key: key not in all_info, data.keys())

        if uncached_keys:
            log_string = (
                '\n'
                '============================================================\n'
                'Hitting the API for %s to get info on %s user(s)\n'
                'IDs: %s\n'
                '============================================================\n'
            ) % (
                on_behalf_of.username if on_behalf_of else 'the app',
                len(uncached_keys),
                ','.join([str(data[k]) for k in uncached_keys])
            )
            log.info(log_string)

            # If there are uncached keys, fetch the user info for those users
            # in chunks of 100
            t = self.get_api(on_behalf_of)
            user_ids = [data[key] for key in uncached_keys]
            new_info = {}
            for id_group in chunk(user_ids, 100):
                bulk_info = t.users.lookup(user_id=','.join([str(user_id) for user_id in id_group]))

                for info in bulk_info:
                    cache_key = reverse_data[str(info['id'])]
                    new_info[cache_key] = info

            # Store any new information gotten in the cache
            cache.set_many(new_info)

            # Add the new info to the already cached info
            all_info.update(new_info)
        return all_info.values()

    def get_avatar_url(self, user, on_behalf_of):
        user_info = self.get_user_info(user, on_behalf_of)
        url = user_info['profile_image_url']

        url_pattern = '^(?P<path>.*?)(?:_normal|_mini|_bigger|)(?P<ext>\.[^\.]*)$'
        match = re.match(url_pattern, url)
        if match:
            return match.group('path') + '_bigger' + match.group('ext')
        else:
            return url

    def get_full_name(self, user, on_behalf_of):
        user_info = self.get_user_info(user, on_behalf_of)
        return user_info['name']

    def get_bio(self, user, on_behalf_of):
        user_info = self.get_user_info(user, on_behalf_of)
        return user_info['description']

    # ==================================================================
    # User-specific info, from the database, used for authenticating
    # against Twitter on behalf of a specific user
    # ==================================================================
    def get_user_id(self, user):
        try:
            # Assume the first one is the one we want
            social_auth = user.social_auth.all()[0]
        except IndexError:
            # If we don't have any, just return empty
            raise SocialMediaException(
                'User %s is not authenticated with a social media account'
                % (user,))

        if social_auth.provider == 'twitter':
            return social_auth.uid
        else:
            raise SocialMediaException(
                ('Can\'t get info for user %s authenticated with a %r '
                 'provider') % (user, social_auth.provider)
            )

        return extra_data['id']

    def get_user_oauth(self, user):
        try:
            # Assume the first one is the one we want
            social_auth = user.social_auth.all()[0]
        except IndexError:
            # If we don't have any, just return empty
            raise SocialMediaException(
                'User is not authenticated with a social media account')

        if social_auth.provider == 'twitter':
            extra_data = social_auth.extra_data
            access_token = parse_qs(extra_data['access_token'])
        else:
            raise SocialMediaException(
                ('Can\'t get info for a user authenticated with a %r '
                 'provider') % social_auth.provider
            )

        return OAuth(
            access_token['oauth_token'][0],
            access_token['oauth_token_secret'][0],
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET
        )

    # ==================================================================
    # App-specific info, from the database, used for authenticating
    # against Twitter on behalf of the app
    # ==================================================================
    def get_app_oauth(self):
        return OAuth(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_SECRET,
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
        )

    def get_api(self, on_behalf_of=None):
        # If user is None, tweet from the app's account
        if on_behalf_of is None:
            oauth = self.get_app_oauth()
        # Otherwise, tweet from the user's twitter account
        else:
            oauth = self.get_user_oauth(on_behalf_of)

        return Twitter(auth=oauth)

    def get_stream(self, on_behalf_of=None):
        # If user is None, tweet from the app's account
        if on_behalf_of is None:
            oauth = self.get_app_oauth()
        # Otherwise, tweet from the user's twitter account
        else:
            oauth = self.get_user_oauth(on_behalf_of)

        return TwitterStream(auth=oauth)

    # ==================================================================
    # Twitter actions
    # ==================================================================
    def tweet(self, text, on_behalf_of=None, **extra):
        t = self.get_api(on_behalf_of)
        try:
            return True, t.statuses.update(status=text, **extra)
        except TwitterHTTPError as e:
            return False, e.response_data

    def add_favorite(self, on_behalf_of, tweet_id, **extra):
        t = self.get_api(on_behalf_of)
        try:
            return True, t.favorites.create(_id=tweet_id, **extra)
        except TwitterHTTPError as e:
            return False, e.response_data

    def remove_favorite(self, on_behalf_of, tweet_id, **extra):
        t = self.get_api(on_behalf_of)
        try:
            return True, t.favorites.destroy(_id=tweet_id, **extra)
        except TwitterHTTPError as e:
            return False, e.response_data

    def retweet(self, tweet_id, on_behalf_of, **extra):
        t = self.get_api(on_behalf_of)
        try:
            return True, t.statuses.retweet(id=tweet_id, **extra)
        except TwitterHTTPError as e:
            return False, e.response_data

    #
    # Streaming
    #
    def itertweets(self, on_behalf_of=None, **extra):
        s = self.get_stream(on_behalf_of)
        return s.statuses.filter(**extra)


default_twitter_service = TwitterService()
