Querius Client
---
Client code for interacting with the [Querius](https://getquerius.com) API.

### Install
```bash
pip install querius
```

### Usage

```python
from google.cloud import bigquery
from querius import QueriusClient, patch_bq_client_with_querius_client
from pathlib import Path

bq_client = bigquery.Client()
q_client = QueriusClient.from_service_account_path(
    api_url="<querius-url>",
    service_account_path=Path('path/to/key.json'),
    customer_id="<querius-customer-id>",
    timeout_seconds=2
)
patch_bq_client_with_querius_client(bq_client, q_client)
```