from django.conf import settings
from django.test import TestCase
from nose.tools import nottest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from functools import wraps
from os import environ


class SeleniumTestCase (TestCase):
    base_url = 'http://localhost:8000'


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

    is_saucelabs = 'saucelabs' in settings.SELENIUM_COMMAND_EXECUTOR
    is_browserstack = 'browserstack' in settings.SELENIUM_COMMAND_EXECUTOR

    # For SauceLabs
    if is_saucelabs:
        options.setdefault('build', environ.get('TRAVIS_BUILD_NUMBER', 'latest'))
        options.setdefault('tags', [environ.get('TRAVIS_PYTHON_VERSION', 'latest'), 'CI'])
        options.setdefault('tunnel-identifier', environ.get('TRAVIS_JOB_NUMBER', 'latest'))

    # For BrowserStack
    elif is_browserstack:
        options.setdefault('build', environ.get('TRAVIS_BUILD_NUMBER', 'latest'))
        options.setdefault('browserstack.tunnel', True)
        options.setdefault('browserstack.debug', True)
        options.setdefault('newSessionWaitTimeout', 120)
        options.setdefault('Idle timeout', 120)
        options.setdefault('platform', 'Any')

    if 'browserName' not in options and 'browser' in options:
        options['browserName'] = options.pop('browser')

    if options.get('browserName').lower() == 'ie':
        if is_saucelabs:
            options['browserName'] = 'Internet Explorer'
        else:
            options['browserName'] = 'internet_explorer'

    browserName = options.get('browserName').lower()
    if is_saucelabs:
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

    if is_browserstack:
        if browserName == 'internet explorer':
            version = float(options.get('version', '10'))
            options.setdefault('os', 'Windows')
            if version < 8:
                options.setdefault('os_version', 'XP')
            elif version < 10:
                options.setdefault('os_version', '7')
            else:
                options.setdefault('os_version', '8')

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
