import os
import pytest
from playwright.sync_api import sync_playwright

os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')


@pytest.fixture(scope='function')
def django_db_setup(django_db_blocker):
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0)
        call_command('loaddata', 'testapp/fixtures/data.json', verbosity=0)


class Connector:
    def __init__(self, live_server):
        print(f"\nStarting end-to-end test server at {live_server}\n")
        self.live_server = live_server

    def __enter__(self):
        def print_args(msg):
            if msg.type in ['info', 'debug']:
                return
            for arg in msg.args:
                print(arg.json_value())

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()
        self.page.on('console', print_args)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.browser.close()
        self.playwright.stop()


@pytest.fixture(scope='session')
def connector(live_server):
    with Connector(live_server) as connector:
        yield connector
