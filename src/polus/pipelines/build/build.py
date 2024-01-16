""" Compute pipelines builder code. """
import os
from pathlib import Path
import logging

import polus.plugins as pp
from wic.api import Step, Workflow
import polus.pipelines.utils as utils

from .constants import (
    DRIVER,
    COMPUTE_COMPATIBILITY,
    CWL_PATH,
    WIC_PATH,
    COMPUTE_SPEC_PATH
)

logger = logging.getLogger(__file__)

class NotAWicNameError(Exception):
    """Raise if parameter's string does not abide to wic conventions."""


class ConfigFileNotFoundError(FileNotFoundError):
    """Exception raised when the config file is not found."""

    def __init__(self, message="Config file not found"):
        self.message = message
        super().__init__(self.message)


def build_compute_pipeline(config_path: Path) -> Path:
    """Generate a compute pipeline.
    
    Args:
        config_path: path to the pipeline spec.
    
    Returns:
        path to a compute spec.
    """
    workflow = build_workflow(config_path)
    return save_compute_pipeline(workflow)


def build_workflow(config_path: Path) -> Workflow:
    """
    Build a Workflow object from the pipeline spec.

    Args:
        path: path to the configuration file that describe the workflow configuration.
    
    Returns:
        a Workflow object.
    """
    try:
        config = utils.load_yaml(config_path)
    except FileNotFoundError as e:
        raise ConfigFileNotFoundError("Workflow config file not found :" + e.filename)

    workflow_name = config["name"]
    steps_config = config["steps"]

    logger.debug(f"workflow has {len(steps_config)} steps")
    step_names = [next(iter(step.keys())) for step in steps_config]
    logger.debug(f"steps are : {step_names}")

    logger.debug(f"retrieving manifests and creating steps...")
    steps = []
    for step_config in steps_config:
        step = _create_step(step_config)
        steps.append(step)

    logger.debug(f"configuring steps...")
    steps = _configure_steps(steps, steps_config)

    logger.debug(f"compiling workflow...")
    workflow = Workflow(steps, workflow_name, path=WIC_PATH)

    return workflow


def save_compute_pipeline(workflow: Workflow) -> Path:
    """Create a compute workflow specification file from a workflow object.
    
    Args:
        workflow: the workflow object to generate a compute workflow specification from.
    
    Returns:
        the file containing the compute workflow specification.
    """
    workflow_cwl = _compile_workflow_to_cwl(workflow)
    return _save_compute_workflow(workflow, workflow_cwl)


def _compile_workflow_to_cwl(workflow: Workflow) -> Path:
    """Compile a workflow to cwl."""
    workflow_cwl = workflow.compile()
    return workflow_cwl


def _save_compute_workflow(workflow: Workflow, workflow_cwl: Path) -> Path:
    """Save a compute workflow to disk."""
    logger.debug(f"generating compute workflow spec...")
    compute_workflow = convert_to_compute_workflow(workflow, workflow_cwl)
    compute_workflow_path = COMPUTE_SPEC_PATH / f"{workflow.name}.json"
    utils.save_json(compute_workflow, compute_workflow_path)
    logger.debug(f"compute workflow saved at : {compute_workflow_path}")
    return compute_workflow_path


def _configure_steps(steps: list[Step], config):
    """
    Apply workflow configuration for each step.
    If the parameter is of type Path with a link attribute,
    the method will try to link it to this step.
    If the parameter is of type Path with a path attribute,
    the method will generate a path from the provided string.
    """
    for step, step_config in zip(steps, config):
        step_name = next(iter(step_config.keys()))
        for key, value in step_config[step_name]["params"].items():
            # retrieve every param that needs to be linked
            if isinstance(value, dict):
                if value["type"] == "Path" and value.get("link"):
                    linked = False
                    previous_step_name, previous_param_name = value["link"].split(".")
                    # find step that referenced and link them
                    for previous_step in steps:
                        if previous_step.cwl_name == previous_step_name:
                            linked = True
                            step.__setattr__(
                                key, previous_step.__getattribute__(previous_param_name)
                            )
                    if not linked:
                        raise Exception(f"could not link {value} for step {key}")
                elif value["type"] == "Path" and value.get("path"):
                    step.__setattr__(key, Path(value["path"]))
            else:
                step.__setattr__(key, value)
    return steps


def _create_step(step_config):
    """
    Create a step from its manifest.
    """
    step_name = next(iter(step_config.keys()))
    plugin_manifest = step_config[step_name]["plugin"]["manifest"]

    if plugin_manifest:
        manifest = pp.submit_plugin(plugin_manifest)
        # TODO CHECK how plugin name's are renamed to abide to python class name convention is hidden
        # in polus plugin, so we need to apply the same function here (we have cut and pasted the code)
        plugin_classname = name_cleaner(manifest.name)
        plugin_version = manifest.version.version
        # TODO CHECK if that even solves the problem or not.
        # Plugins are not registered right away, but need the interpreter to be restarted.
        # We may have to re-run the script the first time anyhow.
        pp.refresh()
        cwl = pp.get_plugin(plugin_classname, plugin_version).save_cwl(
            CWL_PATH / f"{plugin_classname}.cwl"
        )
        step = Step(cwl)
        logger.debug(f"create {step.cwl_name}")
    else:
        logger.warn(f"no plugin manifest in config for step {step_name}")

    return step

def convert_to_compute_workflow(workflow: Workflow, workflow_cwl: Path):
    """
    Transform a wic generated cwl into a valid compute workflow.
    """
    if not workflow_cwl.exists():
        raise FileNotFoundError(
            f"could not find the generated cwl worflow : {workflow_cwl}"
        )

    workflow_inputs: Path = WIC_PATH / "autogenerated" / (workflow.name + "_inputs.yml")
    if not workflow_inputs.exists():
        raise FileNotFoundError(
            f"could not find the generated cwl worflow inputs : {workflow_inputs}"
        )

    compute_workflow = _convert_to_compute_workflow(
        workflow, cwl_workflow=workflow_cwl, cwl_inputs=workflow_inputs
    )

    return compute_workflow


def _convert_to_compute_workflow(
    workflow: Path,
    cwl_workflow: Path,
    cwl_inputs: Path,
):
    """
    Compute defines its own standard for workflow.
    This function transform a wic generated cwl workflow into
    a compute workflow.
    """

    # workflow definition generated by wic
    compute = utils.load_yaml(cwl_workflow)

    add_missing_workflow_properties(compute, cwl_workflow, cwl_inputs)

    for compute_step_name in compute["steps"]:
        cwl_name = replace_run_with_clt_definition(
            compute["steps"][compute_step_name], workflow
        )

        if COMPUTE_COMPATIBILITY:
            # this is the last constraint that we should eventually be able to relax
            add_step_run_base_command(compute["steps"][compute_step_name], cwl_name)

    return compute


def add_missing_workflow_properties(compute, cwl_workflow, cwl_inputs):
    """
    The current compute API requires extra properties that are not part of the standard
    CWL format.

    We update the compute workflow file accordingly.
    """
    # missing properties
    workflow_name = cwl_workflow.stem
    compute.update({"name": workflow_name})
    compute.update({"driver": DRIVER})

    # workflow inputs generated by wic
    inputs = utils.load_yaml(cwl_inputs)
    compute.update({"cwlJobInputs": inputs})


def add_step_run_base_command(compute_step, cwl_name):
    """
    NOTE : COMPUTE_COMPATIBILITY
    Verify that base command are present in the cwl workflow for each clt.
    This should not be mandatory as each plugin container MUST defined an entrypoint.
    NOTE : the plugin name's and the name of its cwl file must match.
    This is enforced currently by copy and paste the internal polus.plugins name_cleaner
    function.
    TODO Update once it is fixed in polus.plugins
    """
    if "run" in compute_step and "baseCommand" in compute_step["run"]: 
        return
    
    plugin_found = False
    for plugin in pp.list_plugins():
        if plugin == cwl_name:
            plugin_found = True
            baseCommand = pp.get_plugin(plugin).baseCommand
            if not baseCommand:
                raise ValueError(
                    f"not found {plugin}.baseCommand. Check {plugin} plugin.json"
                )
            compute_step["run"]["baseCommand"] = baseCommand
    if not plugin_found:
        raise ValueError(
            f"Plugin not found : {cwl_name} in list of plugins : {pp.list_plugins()}. "
            + f"Make sure the plugin's name in plugin.json is {cwl_name}"
        )

def replace_run_with_clt_definition(compute_step, workflow):
    """
    Update the run field of the workflow by replacing the path to a local clt
    with its full definition, according to compute workflow spec.
    """
    cwl_name = Path(compute_step["run"]).stem
    clt_file = None
    for step in workflow.steps:
        if cwl_name == step.cwl_name:
            clt_path = step.cwl_path
            clt_file = utils.load_yaml(clt_path)
            compute_step["run"] = clt_file
    if not clt_path.exists():
        raise FileNotFoundError(f"missing plugin cwl {step.cwl_name} in {clt_path}")
    return cwl_name

# TODO REMOVE. This is from polus plugins. Polus plugins needs to fix this.
# The problem being that names are rewritten in polus plugins but the manifest is not updated.
# We should either enforce a strict name, generate a standardized handle, or update the manifest
# we send back when submitting plugins.
def name_cleaner(name: str) -> str:
    """Generate Plugin Class Name from Plugin name in manifest."""
    replace_chars = "()<>-_"
    for char in replace_chars:
        name = name.replace(char, " ")
    return name.title().replace(" ", "").replace("/", "_")
