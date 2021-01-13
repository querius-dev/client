import time
from dataclasses import dataclass

import requests

from querius.client import safe_and_quick


def test_simple_function_times_out():
    @dataclass
    class MockClient:
        timeout_seconds: int

        @safe_and_quick(return_on_fail='failed')
        def wait(self, seconds):
            time.sleep(seconds)
            return 'succeeded'

    client = MockClient(timeout_seconds=2)
    started = time.time()
    assert client.wait(1) == 'succeeded'
    assert client.wait(2.1) == 'failed'
    assert client.wait(10) == 'failed'
    ended = time.time()
    assert ended - started < 6


def test_long_request_times_out():
    @dataclass
    class MockClient:
        timeout_seconds: int

        @safe_and_quick(return_on_fail='failed')
        def make_request(self, url):
            requests.get(url)
            return 'succeeded'

    client = MockClient(timeout_seconds=2)
    started = time.time()
    assert client.make_request('http://google.co.uk') == 'succeeded'
    assert client.make_request('http://slowwly.robertomurray.co.uk/delay/10000/url/http://www.google.co.uk') == 'failed'
    ended = time.time()
    assert ended - started <= 4


def test_safely_catch_exception():
    @dataclass
    class MockClient:
        timeout_seconds: int

        @safe_and_quick(return_on_fail='failed')
        def raise_exception(self):
            raise Exception('lalal')

    client = MockClient(timeout_seconds=10)
    assert client.raise_exception() == 'failed'
