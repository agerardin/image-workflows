import pytest
from pathlib import Path
import cwl_utils.parser as cwl_parser
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder,
    run_cwl
)
from urllib.parse import urlparse
from polus.pipelines.workflows.model import CWLArray, CWLTypes


@pytest.mark.parametrize("filename", ["conditional-workflow.cwl"])
def test_load_conditional_wf(test_data_dir: Path, tmp_dir: Path, filename):
    """Test that we can load  a workflow with ScatterFeatureRequirement."""
    
    cwl_file = test_data_dir / filename
    wf = Workflow.load(cwl_file)
    wf.save(tmp_dir)

    assert len(wf.inputs) == 2
    assert len(wf.outputs) == 1

    wf_output = wf.outputs[0]
    assert isinstance(wf_output.type,CWLArray)
    assert wf_output.type.items == CWLTypes.FILE

    wf_input_msg = wf.inputs[0]
    assert isinstance(wf_input_msg.type,CWLArray)
    assert wf_input_msg.type.items == CWLTypes.STRING

    wf_input_should_touch = wf.inputs[1]
    assert wf_input_should_touch.type == CWLTypes.INT

    # test last step has a when clause
    touch_step = wf.steps[-1]
    when_clause = touch_step.when   
    assert when_clause
    # test the clause value
    # TODO we should provide more functionalities around this
    assert when_clause == "$(inputs.should_execute < 1)"
    # check we do have a related workflow input
    assert wf_input_should_touch.id == "should_touch"
    assert touch_step.in_[0].source == wf_input_should_touch.id
     

@pytest.mark.parametrize("filename", ["touch_single.cwl"])
def test_build_conditional_step(test_data_dir: Path,
                          filename: str):
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)

    step_builder = StepBuilder(clt,
        when="$(inputs.should_execute < 1)",
        when_input_names=["should_execute"],
        add_inputs=[{"id": "should_execute",
                    "type": "int"
                    }])
    step = step_builder()

    # Check that we added a new step input.
    assert len(clt.inputs) == 1
    assert len(step.in_) == 2

    # Check this step input has the correct name and type.
    should_execute = [input for input in step.in_ if input.id == "should_execute"][0]
    assert should_execute.type == CWLTypes.INT


def _build_conditional_workflow(test_data_dir, clts, workflows):
    #TODO implemennt a load method in process
    steps = []

    for filename in workflows:
        cwl_file = test_data_dir / filename
        clt = Workflow.load(cwl_file)
        print(clt)
        step_builder = StepBuilder(clt)
        step = step_builder()
        print(step)
        steps.append(step)

    for filename in clts:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        print(clt)
        step_builder = StepBuilder(clt,
            when="$(inputs.should_execute < 1)",
            when_input_names=["should_execute"],
            add_inputs=[{"id": "should_execute",
                        "type": "int"
                        }])
        step = step_builder()
        print(step)
        steps.append(step)

    (step1, step2) = steps
    step2.touchfiles = step1.uppercase_message


    wf_builder = WorkflowBuilder("conditional_workflow_generated", steps=steps)
    wf: Workflow = wf_builder()
    return wf


@pytest.mark.parametrize("clts, workflows", [(["touch_single.cwl"], ["workflow3.cwl"])])
def test_build_and_run_conditional_workflow(test_data_dir: Path, clts: list[str], workflows: list[str]):

    wf = _build_conditional_workflow(test_data_dir, clts, workflows)

    input_count = len(wf.inputs)
    expected_count = 2
    assert input_count == expected_count, f"workflow should have {expected_count} input, got {input_count}." 


@pytest.mark.parametrize("clts, workflows", [(["touch_single.cwl"], ["workflow3.cwl"])])
def test_run_positive(test_data_dir: Path, clts: list[str], workflows: list[str]):
    
    wf = _build_conditional_workflow(test_data_dir, clts, workflows)

    wf_cwl_file = Path(urlparse(wf.id).path)

    input_names = [input.id for input in wf.inputs]
    input_values = [f"--{input_names[0]}=test_message_conditional"]

    should_execute = 0
    input_values += [f"--{input_names[1]}={should_execute}"]
    run_cwl(wf_cwl_file, extra_args=input_values)

    # TODO add assert to check the file has been created.


@pytest.mark.parametrize("clts, workflows", [(["touch_single.cwl"], ["workflow3.cwl"])])
def test_run_negative(test_data_dir: Path, clts: list[str], workflows: list[str]):
    
    wf = _build_conditional_workflow(test_data_dir, clts, workflows)

    wf_cwl_file = Path(urlparse(wf.id).path)

    input_names = [input.id for input in wf.inputs]
    input_values = [f"--{input_names[0]}=test_message_conditional"]

    should_execute = 4
    input_values += [f"--{input_names[1]}={should_execute}"]
    run_cwl(wf_cwl_file, extra_args=input_values)

    # TODO add assert to check the file has not been created.

# TODO IMPLEMENT AND FIX
@pytest.mark.xfail(reason="need fix.")
def run_conditional_workflow_with_config():
    pass
    # step_builder = StepBuilder(wf)
    # wf_step = step_builder()
    # wf_step.in_[0] = "ok"

    # config = wf_step.save_config()

    # run_cwl(Path()/f"{wf.name}.cwl", config_file=config)
