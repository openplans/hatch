"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from time import sleep
from .selenium_utils import selenium_test, SeleniumTestCase


# ============================================================
# The tests!
# ============================================================

class SimpleTest (SeleniumTestCase):
    base_url = 'http://localhost:8000'
    service = 'browserstack'

    def only_show_visible_visionaries_on_home(self, driver):
        """
        Make sure that only users with the visible_on_home flag show up on
        the home page.
        """
        driver.get(self.base_url + "/")
        sleep(10)
        self.assertEqual(4, len(driver.find_elements_by_css_selector(".visionaries-list > li > span > img")))
    test_only_show_visible_visionaries_on_home_ie10      = selenium_test(only_show_visible_visionaries_on_home, browser='IE', version='10.0')
    test_only_show_visible_visionaries_on_home_chrome27  = selenium_test(only_show_visible_visionaries_on_home, browser='Chrome', version='27')
    test_only_show_visible_visionaries_on_home_iphone6   = selenium_test(only_show_visible_visionaries_on_home, browser='iPhone', version='6.0')
    test_only_show_visible_visionaries_on_home_iphone5   = selenium_test(only_show_visible_visionaries_on_home, browser='iPhone', version='5.1')
    test_only_show_visible_visionaries_on_home_android4  = selenium_test(only_show_visible_visionaries_on_home, browser='Android', version='4.0')
    test_only_show_visible_visionaries_on_home_firefox21 = selenium_test(only_show_visible_visionaries_on_home, browser='Firefox', version='21')
