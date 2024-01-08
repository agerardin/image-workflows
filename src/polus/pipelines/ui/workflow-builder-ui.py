import solara
from polus.pipelines.build import build_workflow, generate_compute_workflow
from pathlib import Path
import logging
import sys
import copy
from polus.pipelines.compute import submit_workflow

logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s %(message)s"
)
logging.getLogger("polus.pipelines")


def updateModel(input, value):
    print("my update : ", input, value)
    input.value = value


ui_elements = {}


@solara.component
def PluginTextInput(title, input):
    elt = solara.InputText(
        title,
        value=input.value,
        continuous_update=True,
        on_value=lambda value: updateModel(input, value),
    )
    ui_elements[title] = elt


@solara.component
def PluginCheckbox(title, input):
    elt = solara.Checkbox(
        label=title, value=input.value, on_value=lambda value: updateModel(input, value)
    )
    ui_elements[title] = elt


@solara.component
def PluginPathInput(title, input):
    elt = solara.InputText(
        title,
        value=input.value.as_posix(),
        continuous_update=True,
        on_value=lambda value: updateModel(input, Path(value)),
    )
    ui_elements[title] = elt


def do_generate_compute_workflow():
    global compute_workflow
    compute_workflow = generate_compute_workflow(workflow)
    text.set(f"generated compute workflow at : {compute_workflow}")


def do_reset_workflow():
    text.set("reset workflow configuration")
    for step in workflow_original.steps:
        for input in step.inputs:
            input_type = input.inp_type.__name__
            if input_type != "Path" or not input.linked:
                print("##### ", ui_elements[input.name])
                ui_elements[input.name].value = "RRRRRR"
                print("!!!!! ", ui_elements[input.name])


def do_submit_workflow(compute_workflow):
    submit_workflow(compute_workflow)


def create_ui_element(input):
    title = input.name
    if not input.required:
        title += " (optional)"
    input_type = input.inp_type.__name__
    if input_type == "str":
        PluginTextInput(title, input)
    elif input_type == "Path":
        if not input.linked:
            PluginPathInput(title, input)
    elif input_type == "bool":
        PluginCheckbox(title, input)


@solara.component
def Page():
    for step in workflow.steps:
        plugin_name = step.cwl_name
        with solara.Card(title=plugin_name):
            for input in step.inputs:
                create_ui_element(input)
    with solara.Row():
        solara.Button(
            "Generate Compute Workflow", on_click=do_generate_compute_workflow
        )
        # solara.Button("Reset", on_click=do_reset_workflow)
        if compute_workflow:
            solara.Button(
                "Submit To Compute",
                on_click=lambda: do_submit_workflow(compute_workflow),
            )
    solara.Markdown(f"**Status**: {text.value}")


compute_workflow = None
pipeline_spec_path = Path.cwd() / "config/process/BBBC/BBBC001_process.yaml"
text = solara.reactive(f"Loading spec from  : {pipeline_spec_path}")
workflow = build_workflow(pipeline_spec_path)
workflow_original = copy.deepcopy(workflow)
