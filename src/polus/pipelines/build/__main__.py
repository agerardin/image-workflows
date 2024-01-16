"""Command line Interface for the compute pipeline builder."""


import logging
from pathlib import Path
import os
import typer
from typing_extensions import Annotated
from polus.pipelines.build import build_pipeline

logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

POLUS_LOG = getattr(logging, os.environ.get("POLUS_LOG", "INFO"))
logger = logging.getLogger(__file__)
logger.setLevel(POLUS_LOG)

app = typer.Typer(help="Pipeline Generator.")


@app.command()
def main(pipeline_spec: Annotated[Path, typer.Argument()]):
    logger.debug(f"generating pipeline from spec file: {pipeline_spec}")
    return build_pipeline(pipeline_spec)


if __name__ == "__main__":
    app()
