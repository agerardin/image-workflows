import wic.api.pythonapi as api
import polus.plugins as pp
from pathlib import Path

bbbc_download_url = "https://raw.githubusercontent.com/saketprem/polus-plugins/bbbc_download/utils/bbbc-download-plugin/plugin.json"
filerenaming_url = "https://raw.githubusercontent.com/PolusAI/polus-plugins/f20a2f75264d59af78cfb40b4c3cec118309f7ec/formats/file-renaming-plugin/plugin.json"
ome_converter_url = "https://raw.githubusercontent.com/PolusAI/polus-plugins/master/formats/ome-converter-plugin/plugin.json"
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





# polus plugins
plugin_manifest1 = Path("manifest1")
plugin1 = getPlugin(plugin_manifest1)

# saveToCWL originally
# we can keep as such to remove any dependency between polus plugins and wic api
clt1 = plugin1.translateToCWL()
# wic api
tool1 = getTool(clt1)

# why create a step?
# different model -> step: expect to connect its io
# from a top level worklfow / to top level worklfow / to  another step
# in another word, indieiction for generating the actual step
step1 = getStep(tool1)
plugin_manifest2 = Path("manifest2")
plugin2 = getPlugin(plugin_manifest2)
clt2 = plugin2.translateToCWL()
tool2 = getTool(clt2)
step2 = getStep(tool2)


# Here workflow have fully defined steps to work from.
# what's left is just connecting them
# once we do that, then the children step can connect 
subworkflow = Workflow([step1, step2], "processing")
# pipe plugin1 and 2
plugin1.output = plugin2.input
# define the worklfow input
workflow.input = plugin1.input
# define the workflow output
workflow.output = plugin2.output


plugin_manifest3 = Path("manifest3")
plugin3 = getPlugin(plugin_manifest3)
tool3 = getTool(plugin3)
step3 = getStep(tool3)

# define the workflow
# worklfow io can be connect to it child step
# after the declaration, it can also connect ot a the other steps or the parent worklfow steps.
workflow = Workflow([subworkflow, step3], "multiple experiments")
workflow.input = subworkflow.input
workflow.output = step3.output


# set missing io
# type check for scattering
# this w    orks because subworkflow is string and worklfow is array[string]
# provide input/output values to workflow so it is fully configured
workflow.instance(input=[a,b,c,d],output="/home")






    


