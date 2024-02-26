from pathlib import Path
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder,
    run_cwl
)
from pprint import pprint

CWLTOOL_PATH = Path() / "cwl_updated"
OUTPUT_DIR = Path() / "out"


if __name__ == "__main__":
    # collect clts
    bbbc = CWLTOOL_PATH / "bbbcdownload.cwl"
    rename = CWLTOOL_PATH / "file-renaming.cwl"
    ome_converter = CWLTOOL_PATH / "ome-converter.cwl"
    montage = CWLTOOL_PATH / "montage.cwl"
    image_assembler = CWLTOOL_PATH / "image_assembler.cwl"
    precompute_slide = CWLTOOL_PATH / "precompute_slide.cwl"

    clt_files = [bbbc, rename, ome_converter, montage, image_assembler,precompute_slide]
    clts = [CommandLineTool.load(clt) for clt in clt_files]
    steps = [StepBuilder(clt)() for clt in clts]

    (bbbc, rename, ome_converter, montage, image_assembler, precompute_slide) = steps

    bbbc.name = "BBBC001"

    # FileRenaming config
    rename.filePattern = ".*_{row:c}{col:dd}f{f:dd}d{channel:d}.tif"
    rename.outFilePattern = "x{row:dd}_y{col:dd}_p{f:dd}_c{channel:d}.tif"
    rename.mapDirectory = "map"
    rename.inpDir = bbbc.outDir
    
    ome_converter.filePattern = ".*.tif"
    ome_converter.fileExtension = ".ome.tif"
    ome_converter.inpDir = rename.outDir

    # Montage
    montage.inpDir = ome_converter.outDir
    montage.filePattern = "d1_x00_y03_p{p:dd}_c0.ome.tif"
    montage.layout = "p"
    # montage.flipAxis = "[]"
    # montage.gridSpacing = "10"
    # montage.imageSpacing = '4'

    # Image Assembler
    image_assembler.imgPath = ome_converter.outDir
    image_assembler.stitchPath = montage.outDir
    # image_assembler.preview = False
    # image_assembler.timesliceNaming = False

    # # Precompute Slide
    precompute_slide.filePattern = ".*.ome.tif"
    precompute_slide.pyramidType = "Zarr"
    precompute_slide.imageType = "Intensity"
    precompute_slide.inpDir = image_assembler.outDir
    precompute_slide.outDir = Path() / "out"

    workflow = WorkflowBuilder("wf_image_processing", steps = steps)()

    pprint([input.id for input in workflow.inputs])

    # TODO Now the workflow can be configured. We could hide that from the user.
    wf : Workflow = StepBuilder(workflow)()
    config = wf.save_config()

    run_cwl(Path(f"{workflow.name}.cwl"), config_file=config)