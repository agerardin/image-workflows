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
from .constants import SUCCESS_STATUS_CODE

load_dotenv(find_dotenv())

COMPUTE_CLIENT_ID = environ.get("COMPUTE_CLIENT_ID")
COMPUTE_CLIENT_SECRET = environ.get("COMPUTE_CLIENT_SECRET")
TOKEN_URL = environ.get("TOKEN_URL")

# NOTE For now disable HTTPS certificate check
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# logging config
POLUS_LOG = getattr(logging, environ.get("POLUS_LOG", "DEBUG"))
logger = logging.getLogger("polus.pipelines.token_service")
logger.setLevel(POLUS_LOG)


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
    if not TOKEN_URL:
        msg = "you need to set env variable TOKEN_URL"
        raise Exception(msg)
    if not COMPUTE_CLIENT_ID:
        msg = "you need to set env variable COMPUTE_CLIENT_ID"
        raise Exception(msg)
    if not COMPUTE_CLIENT_SECRET:
        msg = "you need to set env variable COMPUTE_CLIENT_SECRET"
        raise Exception(msg)

    token_req_payload = {"grant_type": "client_credentials"}
    auth = (COMPUTE_CLIENT_ID, COMPUTE_CLIENT_SECRET)
    token_response = requests.post(
        TOKEN_URL,
        data=token_req_payload,
        verify=False,  # noqa
        allow_redirects=False,
        auth=auth,
        timeout=REQUESTS_TIMEOUT,
    )

    if token_response.status_code != SUCCESS_STATUS_CODE:
        msg = "Failed to obtain token from the OAuth 2.0 server"
        raise Exception(
            msg,
            token_response,
        )

    token_json = token_response.json()

    access_token = token_json["access_token"]

    if not access_token:
        msg = f"unable to parse access token {token_json}"
        raise Exception(msg)

    return access_token
