"""Command line Interface for the compute pipeline builder."""


import logging
from pathlib import Path
import os
import typer
from typing_extensions import Annotated
from .build import build_compute_pipeline
from ..utils import make_logger

logger = make_logger(__file__)

app = typer.Typer(help="Pipeline Generator.")


@app.command()
def main(pipeline_spec: Annotated[Path, typer.Argument()]):
    logger.debug(f"generating pipeline from spec file: {pipeline_spec}")
    return build_compute_pipeline(pipeline_spec)


if __name__ == "__main__":
    app()
