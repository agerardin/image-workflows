from pathlib import Path
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder,
    run_cwl
)
from pprint import pprint

CWLTOOL_PATH = Path() / "cwl"
OUTPUT_DIR = Path() / "out"


if __name__ == "__main__":
    # collect clts
    bbbc = CWLTOOL_PATH / "BbbcDownload.cwl"
    rename = CWLTOOL_PATH / "FileRenaming.cwl"
    ome_converter = CWLTOOL_PATH / "OmeConverter.cwl"
    montage = CWLTOOL_PATH / "Montage.cwl"
    image_assembler = CWLTOOL_PATH / "ImageAssembler.cwl"
    precompute_slide = CWLTOOL_PATH / "PrecomputeSlide.cwl"

    # clt_files = [bbbc, rename, ome_converter, montage, image_assembler,precompute_slide]
    clt_files = [bbbc, ome_converter]
    clts = [CommandLineTool.load(clt) for clt in clt_files]
    steps = [StepBuilder(clt)() for clt in clts]

    (bbbc, ome_converter) = steps

    bbbc.name = "BBBC001"
    ome_converter.filePattern = ".*.tif"
    ome_converter.fileExtension = ".ome.tif"
    ome_converter.inpDir = bbbc.outDir

    workflow = WorkflowBuilder("wf_image_processing", steps = steps)()

    pprint([input.id for input in workflow.inputs])

    # Now the workflow can be configured. We could hide that from the user.
    wf : Workflow = StepBuilder(workflow)()

    # TODO Change workflow inputs that are linked to populated step should 
    # have their value set automatically!
    wf.wf_image_processing___step_OmeConverter___fileExtension = ".ome.tif"
    wf.wf_image_processing___step_OmeConverter___filePattern = ".*.tif"
    wf.wf_image_processing___step_OmeConverter___outDir = OUTPUT_DIR

    wf.wf_image_processing___step_BbbcDownload___name = "BBBC001"
    # TODO this is a step output (and thus a workflow output)
    # but also a step input (thus a workflow input)
    # For each step output, check if we have corresponding input and remove 
    # this input.
    wf.wf_image_processing___step_BbbcDownload___outDir = OUTPUT_DIR

    # TODO also a bug in config, we need to serialize File and Directory properly!
    # config = wf.save_config()
    config = Path("") / "ref_step_wf_image_processing.yaml"

    run_cwl(Path(f"{workflow.name}.cwl"), config_file=config)