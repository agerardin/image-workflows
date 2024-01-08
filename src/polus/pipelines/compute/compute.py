"""Compute client code."""

import logging
import os
from pathlib import Path

import requests
from dotenv import find_dotenv
from dotenv import load_dotenv
from polus.pipelines import utils
from polus.pipelines.compute.token_service import get_access_token

from .constants import REQUESTS_TIMEOUT
from .constants import UNAUTHORIZED_STATUS_CODE

load_dotenv(find_dotenv())

logger = logging.getLogger("polus.pipelines.compute")

COMPUTE_URL = os.environ.get("COMPUTE_URL")


def submit_pipeline(compute_pipeline_file: Path) -> None:
    """Submit pipeline to a compute instance.

    compute_pipeline_file: path to a pipeline spec.
    """
    token = os.environ.get("ACCESS_TOKEN")
    if not token:
        logger.debug(
            """No access token provided.
                     Requesting new access token.""",
        )
        token = get_access_token()

        if token:
            # store the token for subsequent requests
            os.environ["ACCESS_TOKEN"] = token
    else:
        logger.debug("Use existing access token.")

    if not COMPUTE_URL:
        msg = "COMPUTE_URL env variable not defined."
        raise Exception(msg)

    headers = {"Authorization": f"Bearer {token}"}

    logger.debug(f"sending to compute : {compute_pipeline_file}")
    workflow = utils.load_json(compute_pipeline_file)

    url = COMPUTE_URL + "/compute/workflows"
    r = requests.post(url, headers=headers, json=workflow, timeout=REQUESTS_TIMEOUT)
    logger.debug(r.status_code)
    logger.debug(r.text)

    if r.status_code == UNAUTHORIZED_STATUS_CODE:
        # if we fail to authenticate, get rid of stored token
        del os.environ["ACCESS_TOKEN"]
