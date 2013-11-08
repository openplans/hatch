import re
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Max
from django.db.transaction import commit_on_success
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
        twitter_service.get_users_info(user_group, force_refresh=True)
        first_group_done = True

    log.info('\n*** Done refreshing the user cache. Run me again in a day!\n')


@task
def listen_for_tweets():

    log.info('\n*** Listening for tweets...\n')

    streaming_keywords = settings.STREAMING_KEYWORDS
    keywords_pattern = '|'.join(streaming_keywords)

    # User on most recent tweets
    recent_tweets = Tweet.objects.all()\
        .values('tweet_user_id', 'tweet_user_screen_name')\
        .annotate(most_recent=Max('created_at'))\
        .order_by('-most_recent')[:5000]

    user_ids = [tweet['tweet_user_id'] for tweet in recent_tweets if tweet['tweet_user_id']]

    stream_params = {}
    if streaming_keywords:
        stream_params['track'] = ','.join(streaming_keywords)
    if user_ids:
        stream_params['follow'] = ','.join(user_ids)

    log.info('\nTracking "%s" and following "%s"\n' % (
        ','.join(streaming_keywords),
        ','.join([tweet['tweet_user_screen_name'] for tweet in recent_tweets if tweet['tweet_user_id']])
    ))

    tweets = twitter_service.itertweets(**stream_params)
    for tweet_data in tweets:
        if 'disconnect' in tweet_data:
            msg = tweet_data['disconnect']
            log.info(
                "\n*** Twitter doesn't like you anymore. Reason: %s (%s)\n" %
                (msg.get('reason'), msg.get('code')))
            return

        if 'delete' in tweet_data:
            tweet_data = tweet_data['delete']['status']
            try:
                tweet = Tweet.objects.get(tweet_id=tweet_data['id'])
            except Tweet.DoesNotExist:
                continue
            else:
                log.info('\n*** Twitter wants us to delete a tweet. Let\'s comply.\n')
                tweet.delete()
                continue

        log.info('\n  - I see a tweet!: %s; Checking it out.\n' % (tweet_data.get('id', str(tweet_data)),))

        if 'retweeted_status' in tweet_data:
            log.info('\n  - Oh, nevermind, it\'s a retweet.\n')
            continue

        # Now we're interested. Check if we already have it.
        tweet, created = Tweet.objects.create_or_update_from_tweet_data(tweet_data, commit=False)
        log.info('\n  - Imported a tweet: %s!\n' % (tweet,))

        # Do we already have this tweet? This will be the case if someone has
        # entered a vision or a reply through the app UI. In that case, we
        # create a tweet immediately.
        if not created:
            log.info('\n  - Ah, we already have this one. It has been dealt with, I assume.\n')
            continue

        # Is it a reply, and is the tweet it's replying to already assigned?
        # If so, attach this tweet.
        elif tweet.in_reply_to:
            log.info('\n  - It\'s a reply, and we have the original! Let\'s keep it.\n')

            # Since we did not commit the tweet immediately, we don't know
            # whether another process or thread has created in the mean time.
            # Assume it is still new, and just handle the exception if our
            # assumption is wrong.
            try:
                with commit_on_success():
                    tweet.save(force_insert=True)
            except IntegrityError:
                log.info('\n  - Oh, nevermind. Someone got to it before us.\n')
                continue

            if tweet.in_reply_to.is_vision() or tweet.in_reply_to.is_reply():
                log.info('\n  - Even better: we know what conversation it belongs to!\n')
                tweet.make_reply()

        # Otherwise, does it mention any of our keywords?
        elif re.search(keywords_pattern, tweet.tweet_data['text'], flags=re.I):
            log.info('\n  - Mmm, I see those keywords I\'m lookin for. I\'ll keep it.\n')
            tweet.save()

        else:
            log.info('\n  - Bah, it doesn\'t have anything I\'m interested in. Discarding.\n')
            continue

        # If the user is new, bail out of the loop.
        if tweet.pk and tweet_data['user']['id_str'] not in user_ids:
            log.info('\n  - I see a new user, %s! I\'m gonna bail now; bye.\n' % tweet_data['user']['screen_name'])
            break