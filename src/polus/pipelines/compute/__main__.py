from pathlib import Path
import logging
import os
from dotenv import load_dotenv
import typer
from typing_extensions import Annotated
from polus.pipelines.compute import submit_pipeline
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
POLUS_LOG = getattr(logging, os.environ.get("POLUS_LOG", "INFO"))
logger = logging.getLogger("polus.plugins.workflows.compute_client")
logger.setLevel(POLUS_LOG)

app = typer.Typer(help="Compute Client.")

@app.command()
def main(compute_pipeline_file: Annotated[Path, typer.Argument()]):

    compute_pipeline_file = compute_pipeline_file.resolve()

    if not compute_pipeline_file.exists():
        raise FileExistsError("no compute pipeline file has been provided."
                                +f"{compute_pipeline_file} not found.")
    
    # TODO do we have a pydantic model to validate against?
    if not (compute_pipeline_file.is_file() and compute_pipeline_file.suffix == ".json"):
        raise Exception(f"{compute_pipeline_file} is not a valid pipeline file.")
    
    submit_pipeline(compute_pipeline_file)


if __name__ == "__main__":
    app()