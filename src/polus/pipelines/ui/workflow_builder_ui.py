"""Generate ui to edit pipeline parameters."""

import copy
import logging
import sys
from pathlib import Path
from typing import Any

import solara
from polus.pipelines.build import build_workflow
from polus.pipelines.build import generate_compute_workflow
from polus.pipelines.compute import submit_pipeline

from wic.api.pythonapi import CLTInput

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)
logging.getLogger("polus.pipelines")


def update_model(input: CLTInput, value: Any) -> None:  # noqa ANN401
    """Manage all model updates."""
    input.value = value


ui_elements = {}


@solara.component
def PluginTextInput(title: str, input: CLTInput) -> None:  # noqa N802
    """TextInput element."""
    elt = solara.InputText(
        title,
        value=input.value,
        continuous_update=True,
        on_value=lambda value: update_model(input, value),
    )
    ui_elements[title] = elt


@solara.component
def PluginCheckbox(title: str, clt_input: CLTInput) -> None:  # noqa N802
    """Checkbox element."""
    elt = solara.Checkbox(
        label=title,
        value=clt_input.value,
        on_value=lambda value: update_model(clt_input, value),
    )
    ui_elements[title] = elt


@solara.component
def PluginPathInput(title: str, clt_input: CLTInput) -> None:  # noqa N802
    """TextInput element representing a path."""
    elt = solara.InputText(
        title,
        value=clt_input.value.as_posix(),
        continuous_update=True,
        on_value=lambda value: update_model(clt_input, Path(value)),
    )
    ui_elements[title] = elt


def do_generate_compute_workflow() -> None:
    """UI action to generate a compute pipeline."""
    global compute_workflow  # noqa
    compute_workflow = generate_compute_workflow(workflow)
    text.set(f"generated compute workflow at : {compute_workflow}")


# def do_reset_workflow() -> None:
#     """UI action to reset the config to original values."""
#     text.set("reset workflow configuration")
#     for step in workflow_original.steps:
#         for clt_input in step.inputs:
#             input_type = clt_input.inp_type.__name__
#             if input_type != "Path" or not clt_input.linked:
#                 ui_elements[clt_input.name].value = ""


def do_submit_pipeline(compute_workflow: Path) -> None:
    """UI action to submit a pipeline to a compute instance."""
    submit_pipeline(compute_workflow)


def create_ui_element(clt_input: CLTInput) -> None:
    """Factory function for all UI elements."""
    title = clt_input.name
    if not clt_input.required:
        title += " (optional)"
    input_type = clt_input.inp_type.__name__
    if input_type == "str":
        PluginTextInput(title, clt_input)
    elif input_type == "Path":
        if not clt_input.linked:
            PluginPathInput(title, clt_input)
    elif input_type == "bool":
        PluginCheckbox(title, clt_input)


@solara.component
def Page() -> None:  # noqa N802
    """Represent a Page component."""
    for step in workflow.steps:
        plugin_name = step.cwl_name
        with solara.Card(title=plugin_name):
            for inp in step.inputs:
                create_ui_element(inp)
    with solara.Row():
        solara.Button(
            "Generate Compute Workflow",
            on_click=do_generate_compute_workflow,
        )
        if compute_workflow:
            solara.Button(
                "Submit To Compute",
                on_click=lambda: do_submit_pipeline(compute_workflow),
            )
    solara.Markdown(f"**Status**: {text.value}")


compute_workflow = None
pipeline_spec_path = Path.cwd() / "config/process/BBBC/BBBC001_process.yaml"
text = solara.reactive(f"Loading spec from  : {pipeline_spec_path}")
workflow = build_workflow(pipeline_spec_path)
workflow_original = copy.deepcopy(workflow)
