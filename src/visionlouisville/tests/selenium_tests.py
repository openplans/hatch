"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from .selenium_tools import selenium_test


# ============================================================
# The tests!
# ============================================================

class SimpleTest (TestCase):
    def do_get_app(self, driver):
        driver.get("http://localhost:8000/")
        print driver.title
    test_get_app_ie10 = selenium_test(do_get_app, browser='IE', version='10.0')
    test_get_app_chrome27 = selenium_test(do_get_app, browser='Chrome', version='27')
    test_get_app_iphone6 = selenium_test(do_get_app, browser='iPhone', version='6')
    test_get_app_iphone5 = selenium_test(do_get_app, browser='iPhone', version='5.1')
    test_get_app_android4 = selenium_test(do_get_app, browser='Android', version='4.0')
    test_get_app_firefox21 = selenium_test(do_get_app, browser='Firefox', version='21')

