from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now, timedelta
from visionlouisville.tasks import listen_for_moments

from twitter import TwitterHTTPError
from ssl import SSLError

from time import sleep
from logging import getLogger
log = getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = 'Import new tweets that mention the moment keywords'

    def handle(self, *args, **options):
        while True:
            try:
                last_connect_attempt_time = now()
                listen_for_moments()
                reconnect_delay = 0

            except SSLError as e:
                log.error('\n*** Received an SSL error while streaming from '
                          'Twitter: %s\n' % (e,))

                since_last_connect_attempt = now() - last_connect_attempt_time
                if since_last_connect_attempt > timedelta(seconds=10):
                    reconnect_delay = 0
                elif reconnect_delay < 16:
                    reconnect_delay += 0.25

            except TwitterHTTPError as e:
                log.error('\n*** Received an HTTP error while streaming from '
                          'Twitter: %s\n' % (e,))

                since_last_connect_attempt = now() - last_connect_attempt_time
                if e.e.code == 420:
                    if since_last_connect_attempt > timedelta(seconds=10):
                        reconnect_delay = 60
                    else:
                        reconnect_delay *= 2
                else:
                    if since_last_connect_attempt > timedelta(seconds=10):
                        reconnect_delay = 5
                    elif reconnect_delay < 320:
                        reconnect_delay *= 2

            except KeyboardInterrupt:
                log.info('\n *** Exiting\n')
                return

            log.info('\n*** Sleeping %s seconds before retrying\n' % (reconnect_delay,))
            sleep(reconnect_delay)
            log.info('\n*** Restarting listener\n')
