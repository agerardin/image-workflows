from pathlib import Path
import cwl_utils.parser as cwl_parser
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder,
    run_cwl
)
from urllib.parse import urlparse
from polus.pipelines.workflows.model import CWLArray, CWLBaseType

def _build_scatter_wf(test_data_dir : Path, tmp_dir : Path, clt_files : list[str]) -> Workflow:
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
    assert wf_input_0.type.items == CWLBaseType.STRING

    for wf_output in wf.outputs:
        assert isinstance(wf_output.type,CWLArray)
        assert wf_output.type.items == CWLBaseType.STRING

    return wf


def test_run_scatter_wf_with_config(test_data_dir: Path,
                          tmp_dir: Path,
                          clt_files: list[str]):
    """Test we can run a workflow with linked scattered steps.
    
    In particular, check that type promotion is properly handled.
    """
    wf = _build_scatter_wf(test_data_dir, tmp_dir, clt_files)
    step_builder = StepBuilder(wf)
    wf_step = step_builder()
    wf_step.in_[0] = ["ok"]

    assert wf.inputs[0].value == "ok"
    config = wf_step.save_config()

    run_cwl(Path()/f"{wf.name}.cwl", config_file=config)

    print(config)


test_run_scatter_wf_with_config(test_data_dir=Path() / Path("tests/workflows/test_data") ,
                                tmp_dir=Path() / Path("examples/workflows"),
                                clt_files=["echo_string.cwl", "uppercase2_wic_compatible3.cwl"])
