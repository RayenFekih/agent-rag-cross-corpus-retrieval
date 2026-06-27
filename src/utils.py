from pathlib import Path

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from google.oauth2 import service_account


def load_service_account_credentials(credentials_path: str):
    credentials_file = Path(credentials_path).expanduser().resolve()

    if not credentials_file.exists():
        raise FileNotFoundError(
            f"Service account file not found: {credentials_file}")

    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_file),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    print("Using service account:", credentials.service_account_email)

    return credentials


def create_discovery_engine_client(
    *,
    location: str,
    credentials,
) -> discoveryengine.SearchServiceClient:
    client_options = (
        ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    return discoveryengine.SearchServiceClient(
        credentials=credentials,
        client_options=client_options,
    )
