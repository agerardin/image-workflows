"""Auth client code."""
import base64
import json
import logging
from os import environ
from typing import Any
import requests
import urllib3
from dotenv import find_dotenv
from dotenv import load_dotenv

from .constants import REQUESTS_TIMEOUT
from .constants import SUCCESS_STATUS_CODES
from .exceptions import MissingEnvironmentVariablesException
from ..utils import make_logger

load_dotenv(find_dotenv())

logger = make_logger(__file__)

# NOTE For now disable HTTPS certificate check
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _b64_decode(data: str) -> str:
    """Decode base64 encoded data."""
    data += "=" * (4 - len(data) % 4)
    return base64.b64decode(data).decode("utf-8")


def _jwt_payload_decode(jwt: str) -> Any:  # noqa
    """Return jwt token payload as json."""
    _, payload, _ = jwt.split(".")
    return json.loads(_b64_decode(payload))


def decode_access_token(access_token: str) -> Any:  # noqa
    """Deserialize base64 encoded access token."""
    return _jwt_payload_decode(access_token)


def get_access_token() -> str:
    """Obtain a new OAuth 2.0 token from the authentication server."""
    compute_client_id = environ.get("COMPUTE_CLIENT_ID")
    compute_client_secret = environ.get("COMPUTE_CLIENT_SECRET")
    token_url = environ.get("TOKEN_URL")

    missing_vars = []
    
    if not token_url:
        missing_vars.append("TOKEN_URL")
    if not compute_client_id:
        missing_vars.append("COMPUTE_CLIENT_ID")
    if not compute_client_secret:
        missing_vars.append("COMPUTE_CLIENT_SECRET")

    if missing_vars:
        raise MissingEnvironmentVariablesException(missing_vars)

    token_req_payload = {"grant_type": "client_credentials"}
    auth = (compute_client_id, compute_client_secret)
    token_response = requests.post(
        token_url,
        data=token_req_payload,
        verify=False,  # noqa
        allow_redirects=False,
        auth=auth,
        timeout=REQUESTS_TIMEOUT,
    )

    if not token_response.status_code in SUCCESS_STATUS_CODES:
        msg = "Failed to obtain token from the OAuth 2.0 server"
        raise CannotObtainTokenException(
            f"{msg}: {token_response}",
        )

    token_json = token_response.json()
    access_token = token_json["access_token"]

    if not access_token:
        raise UnparsableTokenException(token_json)

    return access_token


class UnparsableTokenException(Exception):
    """Raise if unable to parse access token."""
    def __init__(token_json: str):
        msg = f"unable to parse access token {token_json}"
        super().__init__(msg)


class UnauthorizedTokenException(Exception):
    """Raise if cannot authenticate with this access token."""


class CannotObtainTokenException(Exception):
    """Raise if unable to obtain token from the OAuth 2.0 server."""