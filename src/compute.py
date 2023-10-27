from token_service import get_access_token
from pathlib import Path
import json
import requests
import utils 
import logging
import os
from dotenv import load_dotenv
import typer
from typing_extensions import Annotated

load_dotenv(override=True)

logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
POLUS_LOG = getattr(logging, os.environ.get("POLUS_LOG", "INFO"))
logger = logging.getLogger("polus.plugins.compute_client")
logger.setLevel(POLUS_LOG)

app = typer.Typer(help="Compute Client.")

@app.command()
def main(compute_workflow_file: Annotated[Path, typer.Argument()]):
    
    token = get_access_token()

    COMPUTE_URL = os.environ.get("COMPUTE_URL")
    if COMPUTE_URL == None :
        raise Exception(f"COMPUTE_URL env variable not defined.")
    
    compute_workflow_file = compute_workflow_file.resolve()
    
    if not compute_workflow_file.exists():
        raise FileExistsError("no cwl workflow file has been provided."
                              +f"{compute_workflow_file} not found.")
        
    headers = {'Authorization': f"Bearer {token}"}

    # TODO do we have a pydantic model to validate against?
    if not (compute_workflow_file.is_file() and compute_workflow_file.suffix == ".json"):
        raise Exception(f"{compute_workflow_file} is not a valid workflow file.")

    logger.debug(f"sending to compute : {compute_workflow_file}")
    workflow = utils.load_json(compute_workflow_file)

    url = COMPUTE_URL + '/compute/workflows'
    r = requests.post(url, headers=headers, json = workflow)
    logger.debug(r.text)


if __name__ == "__main__":
    app()