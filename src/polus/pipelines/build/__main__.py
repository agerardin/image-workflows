
import logging
from pathlib import Path
import os
import typer
from typing_extensions import Annotated
from polus.pipelines.build import build_workflow, generate_compute_workflow

logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

POLUS_LOG = getattr(logging, os.environ.get("POLUS_LOG", "DEBUG"))
logger = logging.getLogger("polus.plugins.workflows.workflow_generator")
logger.setLevel(POLUS_LOG)

app = typer.Typer(help="Workflow Generator.")

@app.command()
def main(workflow_spec: Annotated[Path, typer.Argument()]):
    logger.debug(f"generating workflow from spec file: {workflow_spec}")
    workflow = build_workflow(configPath=workflow_spec)
    generate_compute_workflow(workflow)

if __name__ == "__main__":
    app()