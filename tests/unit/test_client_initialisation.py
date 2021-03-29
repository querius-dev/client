import json
from pathlib import Path

from querius import QueriusClient


def test_initialising_client_from_json():
    service_account_info = json.loads(Path('fake-service-account.json').read_text())
    config = {
        "customer_id": "test_customer_id",
        "service_account_info": service_account_info,
        "api_url": "test_api_url",
        "timeout_seconds": "test_timeout_seconds"
    }
    QueriusClient.from_json_config(json.dumps(config))
