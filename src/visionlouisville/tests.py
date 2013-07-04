"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings
from nose.tools import nottest


# ============================================================
# Selenium helper functions
# ============================================================

def make_selenium_driver(options):
    """
    Create and return a selenium driver with the given capability options.
    """
    return webdriver.Remote(
        command_executor=settings.SELENIUM_COMMAND_EXECUTOR,
        desired_capabilities=options
    )


@nottest
def selenium_test(func, **options):
    """
    Create a test that runs the given function with the given selenium options.
    The function is expected to be a class instance method that takes a driver
    argument.
    """
    # Set up defaults and process the options
    options.setdefault('name', func.__name__)
    options.setdefault('javascriptEnabled', True)
    options.setdefault('build', environ['TRAVIS_BUILD_NUMBER'])
    options.setdefault('tunnel-identifier', environ['TRAVIS_JOB_NUMBER'])

    if 'browserName' not in options and 'browser' in options:
        options['browserName'] = options.pop('browser')

    if options.get('browserName').lower() == 'ie':
        options['browserName'] = 'Internet Explorer'

    browserName = options.get('browserName').lower()
    if browserName == 'internet explorer':
        assert 'version' in options
        version = float(options['version'])
        if version < 8:
            options.setdefault('platform', 'Windows XP')
        elif version < 10:
            options.setdefault('platform', 'Windows 7')
        else:
            options.setdefault('platform', 'Windows 8')

    elif browserName == 'android':
        options.setdefault('platform', 'Linux')

    elif browserName in ('iphone', 'ipad'):
        assert 'version' in options
        version = float(options['version'])
        if version < 5.1:
            options.setdefault('platform', 'OS X 10.6')
        else:
            options.setdefault('platform', 'OS X 10.8')

    # Create the test function
    @wraps(func)
    def test(self):
        driver = make_selenium_driver(options)
        try:
            func(self, driver)
        finally:
            driver.quit()

    # Make sure it's known as a test, regardless of function name
    test.__test__ = True

    return test


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
