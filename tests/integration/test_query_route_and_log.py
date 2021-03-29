import os
from functools import partial
from pathlib import Path

import pytest
from google.cloud.bigquery import Client

from querius import QueriusClient

STAGING_URL = os.environ['QUERIUS_STAGING_URL']
TEST_CUSTOMER_ID = os.environ['QUERIUS_TEST_CUSTOMER_ID']
INTEGRATION_TEST_PROJECT = os.environ['QUERIUS_INTEGRATION_TEST_PROJECT']


@pytest.fixture
def qclient():
    qclient = QueriusClient.from_service_account_path(
        api_url=STAGING_URL,
        service_account_path=Path('real-key.json'),
        customer_id=TEST_CUSTOMER_ID,
        timeout_seconds=2
    )
    # remove timeout decorators
    qclient.route = partial(qclient.route.__wrapped__, qclient)
    qclient.log_query_stats = partial(qclient.log_query_stats.__wrapped__, qclient)
    return qclient


def test_query_route(qclient):
    result = qclient.route("query never seen before")
    assert result is None


def test_query_log(qclient):
    bq_client = Client(project=INTEGRATION_TEST_PROJECT)
    query_job = bq_client.query("""
    SELECT 
        CAST(FLOOR(100*RAND()) AS INT64) AS random_int,
        *
    FROM
        `bigquery-public-data.covid19_jhu_csse.summary` 
    WHERE
        date = '2020-10-12'
    """)
    query_job.result()
    qclient.log_query_stats(query_job)
