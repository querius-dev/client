from typing import Optional

from google.cloud import secretmanager
from loguru import logger


def get_secret(project: str, name: str, version: str) -> Optional[str]:
    fqn = f"projects/{project}/secrets/{name}/versions/{version}"
    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(name=fqn)
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        logger.error(f"Failed to get secret '{fqn}': {repr(e)}")
