from django.test import TestCase, RequestFactory
from django.contrib import messages
# from django.conf import settings
# from django.core.urlresolvers import reverse
# from django.core.cache import cache
# from ..services import TwitterService
# from ..models import Vision, User, Reply, Tweet
# from social_auth.models import UserSocialAuth
from ..admin import CategoryAdmin
from ..models import Category
from mock import patch
from nose.tools import assert_equal
# import json


class CategoryMessagesTest (TestCase):
    def setUp(self):
        Category.objects.all().delete()

    def tearDown(self):
        Category.objects.all().delete()

    def test_error_message_when_no_categories(self):
        request = RequestFactory().get('/admin/hatch/category/')
        admin_view = CategoryAdmin(Category, None)

        with patch.object(admin_view, 'message_user') as msg:
            admin_view.get_queryset(request)
            assert_equal(msg.call_count, 1)
            args, kwargs = msg.call_args
            assert_equal(kwargs.get('level'), messages.ERROR)

    def test_error_message_when_no_categories_active(self):
        Category.objects.create(name="category1", title="Category", prompt="Category?", active=False)
        Category.objects.create(name="category2", title="Category", prompt="Category?", active=False)

        request = RequestFactory().get('/admin/hatch/category/')
        admin_view = CategoryAdmin(Category, None)

        with patch.object(admin_view, 'message_user') as msg:
            admin_view.get_queryset(request)
            assert_equal(msg.call_count, 1)
            args, kwargs = msg.call_args
            assert_equal(kwargs.get('level'), messages.ERROR)

    def test_warning_message_when_more_than_one_categories_active(self):
        Category.objects.create(name="category1", title="Category", prompt="Category?", active=True)
        Category.objects.create(name="category2", title="Category", prompt="Category?", active=True)

        request = RequestFactory().get('/admin/hatch/category/')
        admin_view = CategoryAdmin(Category, None)

        with patch.object(admin_view, 'message_user') as msg:
            admin_view.get_queryset(request)
            assert_equal(msg.call_count, 1)
            args, kwargs = msg.call_args
            assert_equal(kwargs.get('level'), messages.WARNING)
