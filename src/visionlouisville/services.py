from django.conf import settings
from twitter import Twitter, OAuth


class TwitterService (object):
    def get_avatar_url(self, user):
        if user.pk not in self._user_info_memo:
            self.retrieve_user_info(user)

    def get_app_oauth(self):
        return OAuth(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_SECRET,
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
        )

    def get_user_oauth(self, user):
        social_auth = user.social_auth.all()[0]
        if social_auth.provider == 'twitter':
            extra_data = social_auth.extra_data
            access_token = parse_qs(extra_data['access_token'])

        return OAuth(
            access_token['oauth_token'][0],
            access_token['oauth_token_secret'][0],
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET
        )

    def tweet(self, text, user=None):
        # If user is None, tweet from the app's account
        if user is None: oauth = self.get_app_oauth()
        # Otherwise, tweet from the user's twitter account
        else: oauth = self.get_user_oauth(user)

        t = Twitter(auth=oauth)
        t.statuses.update(status=text)
