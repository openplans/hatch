from celery import task, group
from time import sleep
from .models import User
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
