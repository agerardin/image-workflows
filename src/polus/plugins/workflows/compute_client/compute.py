from polus.plugins.workflows.compute_client.token_service import get_access_token
import requests
import polus.plugins.workflows.utils as utils 
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger("polus.plugins.workflows.compute_client")

load_dotenv(override=True)

def submit_workflow(compute_workflow_file):
    token = get_access_token()

    COMPUTE_URL = os.environ.get("COMPUTE_URL")
    if COMPUTE_URL == None :
        raise Exception(f"COMPUTE_URL env variable not defined.")
        
    headers = {'Authorization': f"Bearer {token}"}

    logger.debug(f"sending to compute : {compute_workflow_file}")
    workflow = utils.load_json(compute_workflow_file)

    url = COMPUTE_URL + '/compute/workflows'
    r = requests.post(url, headers=headers, json = workflow)
    logger.debug(r.text)