"""Compute client code."""

import logging
import os
from pathlib import Path
import requests
from dotenv import (find_dotenv, load_dotenv)

from ..utils import (load_json, make_logger)
from .token_service import (
    get_access_token,
    UnauthorizedTokenException,
    CannotObtainTokenException,
    UnparsableTokenException,
    UnauthorizedTokenException
)
from .constants import (
    REQUESTS_TIMEOUT,
    UNAUTHORIZED_STATUS_CODE,
    SUCCESS_STATUS_CODES
)
from .exceptions import (
    MissingEnvironmentVariablesException,
)

load_dotenv(find_dotenv())

logger = make_logger(__file__)


def submit_pipeline(compute_pipeline_file: Path) -> None:
    """Submit pipeline to a compute instance.

    Args:
        compute_pipeline_file: path to a pipeline spec.

    Raises:
        ConfigError: if client is not configured properly.
        TokenError: if there is problem with authentication.
        ComputeError: if the request to compute is otherwise unsuccessful.
        
    """
    try:
        # check we have have defined a compute instance.
        compute_url = os.environ.get("COMPUTE_URL")
        if not compute_url:
            raise MissingEnvironmentVariablesException(["COMPUTE_URL"])

        # retrieve an existing token or try to obtain a new one.
        token = os.environ.get("ACCESS_TOKEN")
        if not token:
            logger.debug(
                "No access token provided. Attempt to request new access token.",
            )
            token = get_access_token()
            if token:
                # store the token for subsequent requests
                os.environ["ACCESS_TOKEN"] = token
        else:
            logger.debug("Use existing access token.")
    except MissingEnvironmentVariablesException as e:
        raise ConfigError(e)
    except ( UnparsableTokenException,
             CannotObtainTokenException) as e:
        raise TokenError(e)

    headers = {"Authorization": f"Bearer {token}"}
    logger.debug(f"sending to compute : {compute_pipeline_file}")
    workflow = load_json(compute_pipeline_file)
    url = compute_url + "/compute/workflows"
    r = requests.post(url, headers=headers, json=workflow, timeout=REQUESTS_TIMEOUT)
    result = str(r.status_code) + r.text
    if r.status_code == UNAUTHORIZED_STATUS_CODE:
        # if we fail to authenticate, get rid of stored token
        del os.environ["ACCESS_TOKEN"]
        e = UnauthorizedTokenException(f"Cannot use token to authenticate to {compute_url}." +
                                        f"{token}. Maybe it is expired? Please retry.")
        raise TokenError(e)

    if not r.status_code in SUCCESS_STATUS_CODES:
        raise ComputeError(result)
    else:
        logger.info(f"successfully sent workflow to compute.")
    

class ComputeError(Exception):
    """Compute Error"""


class ConfigError(Exception):
    """Config Error"""


class TokenError(Exception):
    """Token Error"""