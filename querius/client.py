import json
import urllib.parse
from dataclasses import dataclass
from functools import wraps, partial
from pathlib import Path
from typing import Dict, Optional, Any, Callable

from google.auth.transport.requests import AuthorizedSession
from google.cloud import bigquery
from google.cloud.bigquery import QueryJob
from google.oauth2 import service_account
from wrapt_timeout_decorator import timeout
from loguru import logger

from querius.secretmanager import get_secret_json


def safe_and_quick(func: Callable = None, return_on_fail: Any = None):
    if func is None:
        return partial(safe_and_quick, return_on_fail=return_on_fail)

    @wraps(func)
    def method_wrapper(self, *args, **kwargs):
        try:
            return timeout(self.timeout_seconds)(func)(self, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Call to Querius failed: {repr(e)}")
            return return_on_fail

    return method_wrapper


@dataclass
class QueriusClient:
    customer_id: str
    credentials: service_account.IDTokenCredentials
    api_url: str
    timeout_seconds: int

    @classmethod
    def from_gcp_secret_manager(
            cls,
            api_url: str,
            timeout_seconds: str,
            secret_project: str,
            secret_name: str,
            secret_version: str = 'latest',
    ) -> Optional:
        config = get_secret_json(secret_project, secret_name, secret_version)
        if not config:
            return
        config['api_irl'] = api_url
        config['timeout_seconds'] = timeout_seconds
        return cls.from_service_account_info(**config)

    @classmethod
    def from_service_account_info(
            cls,
            customer_id: str,
            service_account_info: dict,
            api_url: str,
            timeout_seconds: int,
    ):
        return cls(
            customer_id,
            service_account.IDTokenCredentials.from_service_account_info(
                service_account_info,
                target_audience=api_url
            ),
            api_url,
            timeout_seconds
        )

    @classmethod
    def from_service_account_path(
            cls,
            customer_id: str,
            service_account_path: Path,
            api_url: str,
            timeout_seconds: int,
    ):
        return cls.from_service_account_info(
            customer_id,
            json.loads(service_account_path.read_text()),
            api_url,
            timeout_seconds
        )

    @safe_and_quick(return_on_fail=[None, None])
    def route(self, query) -> (Optional[str], Optional[str]):
        logger.debug("Routing query...")
        response = self._request('post', endpoint='/route', data={"query": query}).json()
        logger.debug("Routed ✅")
        return response['project_id'], response['request_id']

    @safe_and_quick
    def log_query_stats(self, query_job: QueryJob, request_id: Optional[str]):
        logger.debug("Logging query...")
        data = {
            'query_job_properties': query_job._properties,
            'python_bigquery_version': bigquery.__version__,
            'request_id': request_id
        }
        self._request('put', endpoint='/log', data=data)
        logger.debug("Logged ✅")

    def fetch_report(self):
        logger.debug("Fetching report...")
        result = self._request('get', endpoint='/report')
        logger.debug("Report fetched ✅")
        return result.json()

    def check_connection(self):
        logger.debug("Checking connection...")
        response = self._request('get', endpoint='/')
        logger.debug("Checked ✅")
        assert response.json() == {'status': 'ok'}

    def _get_authorised_session(self):
        authed_session = AuthorizedSession(self.credentials)
        return authed_session

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None):
        session = self._get_authorised_session()
        session.headers.update({'customer-id': self.customer_id})
        response = session.request(method, urllib.parse.urljoin(self.api_url, endpoint), json=data)
        response.raise_for_status()
        return response
