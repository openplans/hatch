from django.conf import settings
from celery import task
from time import sleep
from .models import User, Tweet
from .utils import chunk
from .services import default_twitter_service as twitter_service

import logging
log = logging.getLogger(__name__)


@task
def refresh_users():

    log.info('\n*** Refreshing user cache\n')

    first_group_done = False
    for user_group in chunk(User.objects.all(), 100):

        if first_group_done:
            log.info('\n  - Waiting 60 seconds before next group\n')
            sleep(60)

        log.info('\n  - Downloading info for group of %s user(s)\n' %
                 (len(user_group),))
        twitter_service.get_users_info(user_group)
        first_group_done = True

    log.info('\n*** Done refreshing the user cache. Run me again in a day!\n')


@task
def listen_for_tweets():

    log.info('\n*** Listening for tweets...\n')

    streaming_keywords = ','.join(settings.STREAMING_KEYWORDS)
    tweets = twitter_service.itertweets(track=streaming_keywords)
    for tweet_data in tweets:
        if 'disconnect' in tweet_data:
            msg = tweet_data['disconnect']
            log.info(
                "\n*** Twitter doesn't like you anymore. Reason: %s (%s)\n" %
                (msg.get('reason'), msg.get('code')))
            break

        log.info('\n  - I see a tweet!: %s; Checking it out.\n' % (tweet_data.get('id', str(tweet_data)),))

        if 'retweeted_status' in tweet_data:
            log.info('\n  - Oh, nevermind, it\'s a retweet.\n')
            continue

        # Now we're interested. Check if we already have it.
        tweet, created = Tweet.objects.create_or_update_from_tweet_data(tweet_data)
        log.info('\n  - Imported a tweet!\n' % (tweet,))
