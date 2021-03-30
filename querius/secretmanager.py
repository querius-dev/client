import json
from typing import Optional

from google.cloud import secretmanager
from loguru import logger


def get_secret_json(project: str, name: str, version: str) -> Optional[dict]:
    """Fetch a JSON secret from GCP Secret Manager."""
    fqn = f"projects/{project}/secrets/{name}/versions/{version}"
    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(name=fqn)
        decoded = response.payload.data.decode('unicode_escape')
        return json.loads(decoded)
    except Exception as e:
        logger.error(f"Failed to get secret '{fqn}': {repr(e)}")
