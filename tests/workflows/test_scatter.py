import pytest
from pathlib import Path
import cwl_utils.parser as cwl_parser
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder,
    run_cwl
)

from urllib.parse import urlparse
from polus.pipelines.workflows.model import CWLArray, CWLBasicType, CWLBasicTypeEnum, CWLType

@pytest.mark.parametrize("filename", ["scatter-workflow2.cwl"])
def test_load_scatter_wf(test_data_dir: Path, tmp_dir: Path, filename):
    """Test that we can load  a workflow with ScatterFeatureRequirement."""
    
    cwl_file = test_data_dir / filename
    scatter_wf = Workflow.load(cwl_file)
    scatter_wf.save(tmp_dir)

    assert len(scatter_wf.inputs) == 1
    assert len(scatter_wf.outputs) == 1

    wf_output = scatter_wf.outputs[0]
    assert isinstance(wf_output.type,CWLArray)
    assert wf_output.type.items.type == CWLBasicTypeEnum.FILE

    wf_input = scatter_wf.inputs[0]
    assert isinstance(wf_input.type,CWLArray)
    assert wf_input.type.items.type == CWLBasicTypeEnum.STRING

    # Check we do have a scatter feature requirement
    assert "ScatterFeatureRequirement" in set(
        [req['class'] for req in scatter_wf.requirements]
        )



@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_build_scatter_step(test_data_dir: Path,
                          filename: str):
    """Test we can build a step with scattered inputs.
    
    In particular, check that type promotion is properly handled.
    """
    
    cwl_file = test_data_dir / filename
    clt = CommandLineTool.load(cwl_file)
    step_builder = StepBuilder(clt)
    step1 = step_builder()

    assert len(step1.in_) == 1
    assert len(step1.out) == 1

    # type checks
    assert step1.message.type == CWLBasicType(type=CWLBasicTypeEnum.STRING)
    assert step1.message_string.type == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    # check value assignment
    step1.message = "test_message"

    # build a scatter step
    scattered_inputs = [input.id for input in clt.inputs]
    step_builder = StepBuilder(clt, scatter=scattered_inputs)
    step1 = step_builder()

    assert len(step1.in_) == 1
    assert len(step1.out) == 1

    # type promotion on scatter
    assert isinstance(step1.message.type,CWLArray)
    assert step1.message.type.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)
    assert isinstance(step1.message_string.type,CWLArray)
    assert step1.message_string.type.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    step1.message = ["test_message"]


@pytest.mark.parametrize("clt_files", [["echo_string.cwl", "uppercase2_wic_compatible3.cwl"]])
def test_build_scatter_wf(test_data_dir: Path,
                          tmp_dir: Path,
                          clt_files: list[str]):
    """Test we can build a workflow with linked scattered steps.
    
    In particular, check that type promotion is properly handled.
    """
    __test_build_scatter_wf(test_data_dir, tmp_dir, clt_files)


def __test_build_scatter_wf(test_data_dir : Path, tmp_dir : Path, clt_files : list[str]) -> Workflow:
    clts = []
    for filename in clt_files:
        cwl_file = test_data_dir / filename
        clt = CommandLineTool.load(cwl_file)
        clts.append(clt)

    (echo, uppercase) = clts

    # build scatter steps
    scattered_inputs = [input.id for input in echo.inputs]
    step_builder = StepBuilder(echo, scatter=scattered_inputs)
    step1 = step_builder()

    scattered_inputs = [input.id for input in uppercase.inputs]
    step_builder2 = StepBuilder(uppercase, scatter=scattered_inputs)
    step2 = step_builder2()

    # linking scattered steps
    step2.message = step1.message_string
    # TODO FIX - UGLY MESSAGE WHEN THIS ATTRIBUTE IS NOT PRESENT!
    # create a test for that
    # step2.uppercase_message = step1.message_string

    wf_builder = WorkflowBuilder("wf_scatter", steps=[step1, step2])
    wf = wf_builder()

    assert len(wf.inputs) == 1
    assert len(wf.outputs) == 2
    
    wf_input_0 = wf.inputs[0]
    assert isinstance(wf_input_0.type,CWLArray)
    assert wf_input_0.type.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    for wf_output in wf.outputs:
        assert isinstance(wf_output.type,CWLArray)
        assert wf_output.type.items == CWLBasicType(type=CWLBasicTypeEnum.STRING)

    return wf

@pytest.mark.parametrize("clt_files", [["echo_string.cwl", "uppercase2_wic_compatible3.cwl"]])
def test_run_scatter_wf(test_data_dir: Path,
                          tmp_dir: Path,
                          clt_files: list[str]):
    """Test we can run a workflow with linked scattered steps.
    
    In particular, check that type promotion is properly handled.
    """
    wf = __test_build_scatter_wf(test_data_dir, tmp_dir, clt_files)

    wf_cwl_file = Path(urlparse(wf.id).path)

    input_names = [input.id for input in wf.inputs]
    input_values = [f"--{input_names[0]}=test_message{i}" for i in range(4)]
    run_cwl(wf_cwl_file, extra_args=input_values)


@pytest.mark.parametrize("clt_files", [["echo_string.cwl", "uppercase2_wic_compatible3.cwl"]])
def test_run_scatter_wf_with_config(test_data_dir: Path,
                          tmp_dir: Path,
                          clt_files: list[str]):
    """Test we can run a workflow with linked scattered steps.
    
    In particular, check that type promotion is properly handled.
    """
    wf = __test_build_scatter_wf(test_data_dir, tmp_dir, clt_files)
    step_builder = StepBuilder(wf)
    wf_step = step_builder()
    wf_step.in_[0].value = ["test_message"]
    
    config = wf_step.save_config()

    run_cwl(Path()/f"{wf.name}.cwl", config_file=config)

    print(config)

