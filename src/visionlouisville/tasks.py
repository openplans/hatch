from django.conf import settings
from celery import task, group
from time import sleep
from .models import User, Moment
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

        log.info('\n  - Downloading info for group of %s user(s)\n' % (len(user_group),))
        twitter_service.get_users_info(user_group)
        first_group_done = True

    log.info('\n*** Done refreshing the user cache. Run me again in a day!\n')

@task
def listen_for_moments():

    log.info('\n*** Listening for moments...\n')

    tweets = twitter_service.itertweets(track=','.join(settings.MOMENT_KEYWORDS))
    for tweet in tweets:
        log.info('\n  - I see a tweet!: %s\n' % (tweet['id'],))
        tweet_media = tweet.get('entities', {}).get('media', [])
        if any(m['type'] == 'photo' for m in tweet_media):
            # Now we're interested. Check if we already have it.
            moment, created = Moment.objects.create_or_update_from_tweet(tweet)
            if created:
                log.info('\n  - Created a new moment "%s"\n' % (moment,))
            else:
                log.info('\n  - Modified an existing moment "%s"\n' % (moment,))
        else:
            log.info('\n  - Nevermind, not interested.\n')
