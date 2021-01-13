import os
from pathlib import Path

import pytest
from google.auth.exceptions import RefreshError
from requests import HTTPError

from querius import QueriusClient

STAGING_URL = os.environ['QUERIUS_STAGING_URL']
TEST_CUSTOMER_ID = os.environ['QUERIUS_TEST_CUSTOMER_ID']


def test_service_account_without_access():
    client = QueriusClient.from_service_account_path(
        api_url=STAGING_URL,
        service_account_path=Path('key-with-no-access.json'),
        customer_id='fake_id',
        timeout_seconds=2
    )
    with pytest.raises(HTTPError) as e:
        client.check_connection()
    assert e.value.response.status_code == 403


def test_fake_service_account():
    client = QueriusClient.from_service_account_path(
        api_url=STAGING_URL,
        service_account_path=Path('fake-key.json'),
        customer_id='fake_id',
        timeout_seconds=2
    )
    with pytest.raises(RefreshError) as e:
        client.check_connection()


def test_check_connection_real_auth_fake_key():
    client = QueriusClient.from_service_account_path(
        api_url=STAGING_URL,
        service_account_path=Path('real-key.json'),
        customer_id='fake_id',
        timeout_seconds=2
    )
    with pytest.raises(HTTPError) as e:
        client.check_connection()
    assert e.value.response.status_code == 403


def test_check_connection_real_auth_real_key():
    client = QueriusClient.from_service_account_path(
        api_url=STAGING_URL,
        service_account_path=Path('real-key.json'),
        customer_id=TEST_CUSTOMER_ID,
        timeout_seconds=2
    )
    client.check_connection()
