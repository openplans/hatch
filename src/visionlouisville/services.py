from django.conf import settings
from django.core.cache import cache
from twitter import Twitter, OAuth
from urlparse import parse_qs


class SocialMediaException (Exception):
    pass


class TwitterService (object):

    def get_user_cache_key_prefix(self, user):
        return 'user-%s' % user.pk

    def get_user_cache_key(self, user, extra):
        return ':'.join([self.get_user_cache_key_prefix(user), extra])

    def get_user_info(self, user):
        cache_key = self.get_user_cache_key(user, 'info')
        info = cache.get(cache_key)

        if info is None:
            t = self.get_api(user)
            info = t.users.show(user_id=self.get_user_id(user))
            info = dict(info.items())  # info is a WrappedTwitterResponse
            cache.set(cache_key, info)
        return info

    def get_avatar_url(self, user):
        user_info = self.get_user_info(user)
        return user_info['profile_image_url']

    def get_user_id(self, user):
        try:
            # Assume the first one is the one we want
            social_auth = user.social_auth.all()[0]
        except IndexError:
            # If we don't have any, just return empty
            raise SocialMediaException(
                'User is not authenticated with a social media account')

        if social_auth.provider == 'twitter':
            extra_data = social_auth.extra_data
        else:
            raise SocialMediaException(
                ('Can\'t get info for a user authenticated with a %r '
                 'provider') % social_auth.provider
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

    def get_app_oauth(self):
        return OAuth(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_SECRET,
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
        )

    def get_api(self, user=None):
        # If user is None, tweet from the app's account
        if user is None: oauth = self.get_app_oauth()
        # Otherwise, tweet from the user's twitter account
        else: oauth = self.get_user_oauth(user)

        return Twitter(auth=oauth)

    def tweet(self, text, user=None):
        t = self.get_api()
        t.statuses.update(status=text)
