import polus.plugins as pp
from wic.api import Step, Workflow
from pathlib import Path
import os
from enum import Enum
import polus.pipelines.utils as utils
import re
import requests, zipfile, io
import logging
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

logger = logging.getLogger("polus.plugins.pipelines.build")

# Argo-driver
DRIVER = "argo"
# Generate cwl workflow compatible with the legacy argo-driver
LEGACY_DRIVER = False

# Set to True to run workflow with wic-provided cwl runner.
RUN_LOCAL = False
# Set to True to modify wic-generated workflow to align with Compute restrictions regarding cwl.
COMPUTE_COMPATIBILITY = True

# Current Working Directory
WORKING_DIR = Path(os.getcwd()).absolute()  # preprend to all path to make them absolute

# where to create CLT for the WIC API
CWL_PATH = WORKING_DIR / Path("cwl")
Path(CWL_PATH).mkdir(parents=True, exist_ok=True)

# staging area for wic
WIC_PATH = WORKING_DIR / Path("wic")
Path(WIC_PATH).mkdir(parents=True, exist_ok=True)

# where to create compute workflow
COMPUTE_SPEC_PATH = WORKING_DIR / Path("compute")
Path(COMPUTE_SPEC_PATH).mkdir(parents=True, exist_ok=True)


class DatasetType(Enum):
    BBBC = ("BBBC",)
    NIST_MIST = "NIST_MIST"


class NotAWicNameError(Exception):
    """Raise if parameter's string does not abide to wic conventions."""


class ConfigFileNotFoundError(FileNotFoundError):
    """Exception raised when the config file is not found."""

    def __init__(self, message="Config file not found"):
        self.message = message
        super().__init__(self.message)


def build_pipeline(config_path: Path) -> Path:
    workflow = build_workflow(config_path)
    return generate_compute_workflow(workflow)


def build_workflow(config_path: Path) -> Workflow:
    """
    Build a compute workflow or run the cwl workflow locally,
    depending on the value of the global flag RUN_LOCAL
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


def generate_compute_workflow(workflow: Workflow) -> Path:
    workflow_cwl = compile_workflow_to_cwl(workflow)
    return _save_compute_workflow(workflow, workflow_cwl)


def compile_workflow_to_cwl(workflow: Workflow) -> Path:
    # TODO should be stored in workflow object rather than returned by compile()
    # along with the path to the input yaml file.
    workflow_cwl = workflow.compile()
    return workflow_cwl


def run_workflow_local(workflow: Workflow):
    if RUN_LOCAL:
        logger.debug("running workflow locally with cwl runner...")
        workflow.run(True)


def _save_compute_workflow(workflow: Workflow, workflow_cwl: Path) -> Path:
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
        # TODO use some generic plugin manifest

    return step


def _rewrite_bbbcdowload_outdir_for_compute(compute_workflow, config):
    """
    TODO REMOVE HACK
    Rewrite cwlJobInputs.bbbcdownload___outDir.path with its final value as
    a workaround of how wic create explicit link between step params.
    """

    out_dir = config["outputs"]["bbbcdownload.outDir"]["path"]
    if COMPUTE_COMPATIBILITY:
        directory_attr = "path"
    else:
        directory_attr = "location"
    try:
        path = compute_workflow["cwlJobInputs"]["bbbcdownload___outDir"][directory_attr]
        current_path = Path(path)
        compute_workflow["cwlJobInputs"]["bbbcdownload___outDir"][directory_attr] = (
            current_path / out_dir
        ).as_posix()
    except KeyError:
        raise Exception(
            f"bbbcdownload step not found or does not contain bbbcdownload___outDir"
        )


def convert_to_compute_workflow(workflow: Workflow, workflow_cwl: Path):
    """
    Transform a wic generated cwl into a valid compute workflow
    """
    # TODO workflow_cwl should be stored in the workflow object
    if not workflow_cwl.exists():
        raise FileNotFoundError(
            f"could not find the generated cwl worflow : {workflow_cwl}"
        )

    # TODO should be stored in the workflow object
    workflow_inputs: Path = WIC_PATH / "autogenerated" / (workflow.name + "_inputs.yml")
    if not workflow_inputs.exists():
        raise FileNotFoundError(
            f"could not find the generated cwl worflow inputs : {workflow_inputs}"
        )

    compute_workflow = _convert_to_compute_workflow(
        workflow, cwl_workflow=workflow_cwl, cwl_inputs=workflow_inputs
    )

    return compute_workflow


# TODO create a pydantic model for Compute? Reference it?
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

        if COMPUTE_COMPATIBILITY and DRIVER == "argo" and LEGACY_DRIVER:
            rewrite_io_paths_as_string(compute["steps"][compute_step_name])
            rewrite_location_as_path(compute["cwlJobInputs"])
            add_step_run_id(compute["steps"][compute_step_name], compute_step_name)

    return compute


def add_missing_workflow_properties(compute, cwl_workflow, cwl_inputs):
    # missing properties
    workflow_name = cwl_workflow.stem
    compute.update({"name": workflow_name})
    compute.update({"driver": DRIVER})

    # workflow inputs generated by wic
    inputs = utils.load_yaml(cwl_inputs)
    compute.update({"cwlJobInputs": inputs})


def remove_unused_workflow_properties(compute):
    # workflow['schemas']= workflow['$schemas']
    del compute["$schemas"]
    # workflow['namespaces']= workflow['$namespaces']
    del compute["$namespaces"]
    del compute["class"]
    del compute["cwlVersion"]


def update_wic_value(v):
    try:
        parsed_v = parse_wic_name(v)
        if parsed_v:
            dependency_param = parsed_v[2].split("/")
            if len(dependency_param) == 2:
                new_v = (
                    sanitize_for_compute_argo(dependency_param[0])
                    + "/"
                    + dependency_param[1]
                )
            else:
                new_v = sanitize_for_compute_argo(parsed_v[2])
                if parsed_v[3] != None:
                    new_v = new_v + "___" + parsed_v[3]
            return new_v
    except NotAWicNameError:
        pass  # ignore if not in wic format


def update_wic_values(step):
    for k, v in step.items():
        try:
            parsed_v = parse_wic_name(v)
            if parsed_v:
                dependency_param = parsed_v[2].split("/")
                if len(dependency_param) == 2:
                    new_v = (
                        sanitize_for_compute_argo(dependency_param[0])
                        + "/"
                        + dependency_param[1]
                    )
                else:
                    new_v = sanitize_for_compute_argo(parsed_v[2])
                    if parsed_v[3] != None:
                        new_v = new_v + "___" + parsed_v[3]
                step[k] = new_v
        except NotAWicNameError:
            pass  # ignore if not in wic format


def update_wic_keys(json):
    keys = list(json)
    for k in keys:
        try:
            parsed_k = parse_wic_name(k)
            if parsed_k:
                new_k = sanitize_for_compute_argo(parsed_k[2])
                if parsed_k[3] != None:
                    new_k = new_k + "___" + parsed_k[3]
                json[new_k] = json.pop(k)
        except NotAWicNameError:
            pass  # ignore if not in wic format


def parse_wic_name(wic_name: str):
    param = None
    step_or_param = wic_name.split("___")
    step = step_or_param[0]
    if len(step_or_param) == 2:
        param = step_or_param[1]
    try:
        workflow_name, _, step_index, step_name = step.split("__")
        return workflow_name, step_index, step_name, param
    except:
        raise NotAWicNameError


def rewrite_location_as_path(cwlJobInputs):
    """
    NOTE : COMPUTE_COMPATIBILITY
    Replace Directory `location` attribute with `path`
    """
    for input in cwlJobInputs:
        if (
            isinstance(cwlJobInputs[input], dict)
            and cwlJobInputs[input]["class"] == "Directory"
        ):
            if cwlJobInputs[input].get("location"):
                cwlJobInputs[input]["path"] = cwlJobInputs[input]["location"]
                del cwlJobInputs[input]["location"]


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
    try:
        compute_step["run"]["baseCommand"]
    except KeyError:
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
        raise Exception(f"missing plugin cwl {step.cwl_name} in {clt_path}")
    return cwl_name


def add_step_run_id(compute_step, compute_step_name):
    """
    NOTE this is no longer necessary with the new compute aro-driver
    An id is necessary for compute to process the step correctly.
    Generate id based on the plugin name,
    transformed to abide argo-driver spec for names.
    """
    # contains the step name
    compute_step["run"]["id"] = sanitize_for_compute_argo(compute_step_name)


def rewrite_io_paths_as_string(compute_step):
    """
    NOTE : COMPUTE_COMPATIBILITY
    Compute does not currently support paths object.
    We replace them by strings.
    """
    for input in compute_step["in"]:
        compute_step["in"][input] = compute_step["in"][input]["source"]


def sanitize_for_compute_argo(step_name: str):
    """
    Argo have specific requirements about how it forms its name that differs from
    those of wic.
    Argo abides by Kubernetes naming conventions.
    Step names are supposed to be valid kubernetes container names
    [TODO add link to spec]
    """
    # return step_name.replace("_","-").replace(" ","").lower()
    return step_name


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


def create_nist_mist_dataset(img_path, stitch_path):
    """
    Download the NIST MIST dataset.
    """

    # Make sure the target directories exist
    os.makedirs(img_path, exist_ok=True)
    os.makedirs(stitch_path, exist_ok=True)

    FOVS_URL = (
        "https://github.com/usnistgov/MIST/wiki/testdata/Small_Phase_Test_Dataset.zip"
    )

    STITCHING_VECTOR_URL = "https://github.com/usnistgov/MIST/wiki/testdata/Small_Phase_Test_Dataset_Example_Results.zip"

    r = requests.get(FOVS_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(img_path)
    z.close()

    img_path = img_path / "Small_Phase_Test_Dataset" / "image-tiles/"

    if not img_path.exists:
        raise FileNotFoundError(
            f"could not successfully download nist_mist_dataset images"
        )

    r = requests.get(STITCHING_VECTOR_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(stitch_path)
    z.close()

    stitch_path = (
        stitch_path
        / "Small_Phase_Test_Dataset_Example_Results/img-global-positions-0.txt"
    )

    if not stitch_path.exists:
        raise FileNotFoundError(
            f"could not successfully download nist_mist_dataset stitching vector"
        )

    return img_path, stitch_path.parent


def configure_convert_workflow_nist_mist(
    dataset_name: str, dataset_path: Path, wic_path: Path, out_dir: Path, steps
):
    """
    NOTE each dataset requires its own peculiar set of steps.
    """
    # find Images directory
    image_path = None
    image_files = []
    for dir_path, _, _ in os.walk(dataset_path.absolute() / dataset_name):
        if dir_path.split("/")[-1] == "image-tiles":
            image_path = dir_path
            for _, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".tif"):
                        image_files.append(os.path.join(dir_path, file))
    # TODO remove when the workflow execution will be more robust
    logger.debug(f"path to downloaded images : {image_path}")
    logger.debug(f"tif files downloaded : {image_files}")

    # single well. Take last part. A is well row, 03 well column, p position, d channel.
    # TODO CHECK run in isolation to verify behavior
    nist_mist = {
        "name": "NIST_MIST",
        "ome_filePattern": ".*.tif",
        "rename_filePattern": "img_r{row:ddd}_c{col:ddd}.tif",
        "rename_outFilePattern": "img_r{row:ddd}_c{col:ddd}.tif",
    }

    if not image_path:
        raise Exception(f"Could not find {image_path} directory in {dataset_path}")

    filerenaming, omeconverter = steps

    filerenaming.inpDir = Path(image_path)
    filerenaming.filePattern = nist_mist["rename_filePattern"]
    filerenaming.outFilePattern = nist_mist["rename_outFilePattern"]
    filerenaming.fileExtension = ".tif"
    # filerenaming.mapDirectory= 'raw'

    omeconverter.inpDir = filerenaming.outDir
    # TODO REPORT bad filepattern just crash with error 1. Better reporting needed
    omeconverter.filePattern = nist_mist["ome_filePattern"]
    omeconverter.fileExtension = ".ome.tif"
    omeconverter.outDir = out_dir

    WFNAME_convert = "workflow_convert_" + dataset_name
    return Workflow(steps, WFNAME_convert, path=wic_path.absolute())


def recycle_stitching_vector(stitch_path: Path, out_dir: Path, prepend: str):
    """
    Temporary method that rewrite the stitching vectors according to the modifications made by
    the ome-converter/filerenaming workflow.
    """
    for vector in stitch_path.iterdir():
        with open(vector, "r") as file:
            output_vector = out_dir / vector.name
            with open(output_vector, "w") as output_file:
                # bad for very large files, replace with a stream api
                lines: list[str] = file.readlines()
                for line in lines:
                    line = line.replace(".tif", ".ome.tif")
                    pattern = "([a-zA-Z_0-9])+.ome.tif"
                    result = re.search(pattern, line)
                    if result:
                        line = re.sub(pattern, prepend + result.group(), line)
                        output_file.write(line)
