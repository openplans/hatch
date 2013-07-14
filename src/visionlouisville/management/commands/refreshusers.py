from django.core.management.base import BaseCommand, CommandError
from visionlouisville.tasks import refresh_users

from logging import getLogger
log = getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Request information on all users from Twitter, updating the user info cache'

    def handle(self, *args, **options):
        refresh_users()
