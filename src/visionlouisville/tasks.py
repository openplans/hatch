from django.conf import settings
from celery import task
from time import sleep
from .models import User, Vision
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
    for tweet in tweets:
        if 'disconnect' in tweet:
            msg = tweet['disconnect']
            log.info(
                "\n*** Twitter doesn't like you anymore. Reason: %s (%s)\n" %
                (msg.get('reason'), msg.get('code')))
            break

        log.info('\n  - I see a tweet!: %s; Checking it out.\n' % (tweet.get('id', str(tweet)),))

        if 'retweeted_status' in tweet or tweet.get('text', '').startswith('RT'):
            log.info('\n  - Oh, nevermind, it\'s a retweet.\n')
            continue

        tweet_media = tweet.get('entities', {}).get('media', [])
        if any(m['type'] == 'photo' for m in tweet_media):
            # Now we're interested. Check if we already have it.
            vision, created = Vision.objects.create_or_update_from_tweet(tweet)
            if created:
                log.info('\n  - Created a new vision "%s", yay!\n' % (vision,))
            else:
                log.info('\n  - Modified a vision "%s", yay!\n' % (vision,))
        else:
            log.info('\n  - Eh, there\'s no photos in it. Not interested.\n')
