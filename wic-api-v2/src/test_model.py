import yaml
from pathlib import Path
import cwl_utils.parser as cwl_parser
from model import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder
)
import logging
from rich import print
import filecmp
import tempfile
import shutil

logger = logging.getLogger()

def test_parsing_doc_with_special_character_string():
    """Test that docstring with |- are taken care of."""
    NotImplemented

def test_cwl():
    """Test model roundtrip to check for loss of information
    when serializing our model.
    ."""
    # TODO create a set of parameters so we can test various clts
    echo_string_file = Path("tests/echo_string.cwl")

    # We need ref file generated from the cwlparser only
    # and a roundtrip file coming from our model
    data_dir = Path(tempfile.mkdtemp(suffix="test_data"))
    ref_filepath = Path(data_dir) / "ref_echo_string.cwl"
    roundtrip_filepath = Path(data_dir) / "round_trip_echo_string.cwl"

    # ref file from cwlparser
    ref_model = cwl_parser.load_document_by_uri(echo_string_file)
    serialized_ref_model = cwl_parser.save(ref_model)
    with ref_filepath.open("w", encoding="utf-8") as ref_file:
        ref_file.write(yaml.dump(serialized_ref_model))

    # Our model is saved, then reloaded with cwlparser
    new_model = CommandLineTool.load(echo_string_file)
    new_model_file = new_model.save()
    roundtrip_model = cwl_parser.load_document_by_uri(new_model_file)
    serialized_roundtrip_model = cwl_parser.save(roundtrip_model)
    
    # Check the models are identical
    with roundtrip_filepath.open("w", encoding="utf-8") as roundtrip_file:
        roundtrip_file.write(yaml.dump(serialized_roundtrip_model))
    
    assert filecmp.cmp(ref_filepath,roundtrip_filepath, shallow=False)

    shutil.rmtree(data_dir)


test_cwl()

workflow_file= Path("tests/workflow5.cwl")
wf1 = Workflow.load(workflow_file)
print(wf1)

subworkflow_file = Path("tests/subworkflow1.cwl")
wf2 = Workflow.load(subworkflow_file)
wf2.save()
print(wf2)

# TODO So cwlparser does not check the referenced clts,
# It justs check the definition is valid at the first level.
# So we will need to pull all references first.
# For that, provide a Context object so we parse clts over and over.


# load a clt
echo_file = Path("tests/echo_string.cwl")
echo = CommandLineTool.load(echo_file)
print(echo)

# build a first step
step_builder = StepBuilder(echo)
step1 = step_builder()
print(step1)

# load a second clt
uppercase_file = Path("tests/uppercase2_wic_compatible2.cwl")
uppercase = CommandLineTool.load(uppercase_file)
print(uppercase)

# build our second step
step_builder2 = StepBuilder(uppercase)
step2 = step_builder2()
print(step2)


# NOTE that is simulating the linking between 2 steps ios.
echo_out_message_string = step1.out[0].id
uppercase_in_message = step2.in_[0]
uppercase_in_message.source = step1.id + "/" + echo_out_message_string

echo_out_message_string = step1.out[0].id
uppercase_message_in_message = step2.in_[1]
uppercase_message_in_message.source = step1.id + "/" + echo_out_message_string

print(step1)
print(step2)

wf3_builder = WorkflowBuilder("wf3", steps=[step1, step2])
wf3 = wf3_builder()
print(wf3)

workflow_file2= Path("tests/workflow7.cwl")
wf2 = Workflow.load(workflow_file2)
wf2.save()
print(wf2)

step_builder3 = StepBuilder(wf3)
step3 = step_builder3()
print(step3)

touch_file = Path("tests/touch_single.cwl")
touch = CommandLineTool.load(touch_file)
print(touch)
step_builder_touch = StepBuilder(touch)
touch_step = step_builder_touch()

echo_out_message_string = step3.out[1].id
touch_touchfiles = touch_step.in_[0]
touch_touchfiles.source = step3.id + "/" + echo_out_message_string

wf4_builder = WorkflowBuilder("wf4", steps = [step3, touch_step])
step4 = wf4_builder()

print("--------------")

print(step4)

