import wic.api.pythonapi as api
import polus.plugins as pp
from pathlib import Path

bbbc_download_url = "https://raw.githubusercontent.com/saketprem/polus-plugins/bbbc_download/utils/bbbc-download-plugin/plugin.json"
filerenaming_url = "https://raw.githubusercontent.com/PolusAI/polus-plugins/f20a2f75264d59af78cfb40b4c3cec118309f7ec/formats/file-renaming-plugin/plugin.json"
ome_converter_url = "https://raw.githubusercontent.com/PolusAI/polus-plugins/master/formats/ome-converter-plugin/plugin.json"
estimate_flatfield_url = " https://raw.githubusercontent.com/nishaq503/polus-plugins/master/regression/basic-flatfield-estimation-plugin/plugin.json"
apply_flatfield_url = "https://raw.githubusercontent.com/PolusAI/polus-plugins/master/transforms/images/apply-flatfield-plugin/plugin.json"
montage_url = "https://raw.githubusercontent.com/PolusAI/polus-plugins/master/transforms/images/montage-plugin/plugin.json" 
# need updates
image_assembler_url = "https://raw.githubusercontent.com/agerardin/polus-plugins/new/image-assembler-plugin-1.4.0-dev0/transforms/images/image-assembler-plugin/plugin.json"
precompute_slide_url = "https://raw.githubusercontent.com/agerardin/polus-plugins/update/precompute-slide-fp2/visualization/precompute-slide-plugin/plugin.json"

WIC_STAGING = Path() / "WIC_STAGING"
WIC_STAGING.mkdir(parents=True, exist_ok=True)
CWLTOOL_PATH = (WIC_STAGING / "CWL_TOOLS").resolve()
CWLTOOL_PATH.mkdir(exist_ok=True)
WORKFLOW_PATH = (WIC_STAGING / "WORKFLOWS").resolve()
WORKFLOW_PATH.mkdir(exist_ok=True)
RUNS = (WIC_STAGING / "RUNS").resolve()
RUNS.mkdir(exist_ok=True)


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

def create_step(url: str) -> api.Step:
    manifest = pp.submit_plugin(url)
    plugin_classname = name_cleaner(manifest.name)
    plugin_version = manifest.version.version
    cwl_tool = pp.get_plugin(plugin_classname, plugin_version).save_cwl(
    CWLTOOL_PATH / f"{plugin_classname}.cwl"
    )
    step = api.Step(cwl_tool)
    return step

if __name__ == "__main__":
    rename = create_step(filerenaming_url)
    ome_converter = create_step(ome_converter_url)
    estimate_flatfield = create_step(estimate_flatfield_url)
    apply_flatfield = create_step(apply_flatfield_url)
    montage = create_step(montage_url)
    image_assembler = create_step(image_assembler_url)
    precompute_slide = create_step(precompute_slide_url)

    # FileRenaming config
    rename.filePattern = ".*_{row:c}{col:dd}f{f:dd}d{channel:d}.tif"
    rename.outFilePattern = "x{row:dd}_y{col:dd}_p{f:dd}_c{channel:d}.tif"
    rename.mapDirectory = "map"
    rename.inpDir = Path("/Users/antoinegerardin/Documents/projects/workflow-inference-compiler/FileRenaming")


    # OMEConverter
    ome_converter.filePattern = ".*.tif"
    ome_converter.fileExtension = ".ome.tif"
    ome_converter.inpDir = rename.outDir

    # Estimate Flatfield
    estimate_flatfield.inpDir = ome_converter.outDir
    estimate_flatfield.filePattern = "d1_x00_y03_p{p:dd}_c0.ome.tif"
    estimate_flatfield.groupBy = "p"
    estimate_flatfield.getDarkfield = True

    # Apply Flatfield
    apply_flatfield.imgDir = ome_converter.outDir
    apply_flatfield.img_pattern = "d1_x00_y03_p{p:dd}_c0.ome.tif"
    apply_flatfield.ffDir = estimate_flatfield.outDir
    apply_flatfield.ffPattern = "d1_x00_y03_p{p:dd}_c0_flatfield.ome.tif"
    apply_flatfield.dfPattern = "d1_x00_y03_p{p:dd}_c0_darkfield.ome.tif"
    apply_flatfield.outDir= montage.inpDir
    
    # Montage
    # TODO CHECK with Najib why this would not work
    # montage.inpDir = apply_flatfield.outDir
    montage.inpDir = ome_converter.outDir
    montage.filePattern = "d1_x00_y03_p{p:dd}_c0.ome.tif"
    montage.layout = "p"

    # Image Assembler
    image_assembler.imgPath = ome_converter.outDir
    image_assembler.stitchPath = montage.outDir

    # Precompute Slide
    precompute_slide.pyramidType = "Zarr"
    precompute_slide.imageType = "Intensity"
    precompute_slide.inpDir = image_assembler.outDir
    precompute_slide.outDir = RUNS


    steps = [rename, ome_converter, estimate_flatfield, montage, image_assembler, precompute_slide]
    workflow = api.Workflow(steps, "experiment", WORKFLOW_PATH)
    workflow._save_yaml()

    # TODO CHECK compiling errors are not propagated back to us, so we don't know where to look
    workflow.compile()

    # workflow.run(debug=True)


