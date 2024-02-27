from pathlib import Path
from polus.pipelines.workflows import Process
from rich import print




def test_load_process(test_data_dir: Path, filename: str, recursive = False, context = {}):
    cwl_file = test_data_dir / filename
    wf1 = Process.load(cwl_file, recursive=recursive, context=context)
    # print(wf1)


test_data_dir = Path() / "tests" / "workflows" / "test_data"
# filename = "workflow5.cwl"
# test_load_process(test_data_dir, filename)


# filename = "scatter-workflow1.cwl"
# test_load_process(test_data_dir, filename)


# filename = "nested_types3.cwl"
# test_load_process(test_data_dir, filename)

# filename = "echo_string.cwl"
# test_load_process(test_data_dir, filename)

# filename = "echo_string.cwl"
# test_load_process(test_data_dir, filename, recursive=True)

# filename = "wf_image_processing.cwl"
# test_load_process(test_data_dir, filename, recursive=True)

# filename = "wf_image_processing.cwl"
# context = {}
# test_load_process(test_data_dir, filename, recursive=True, context = context)
# print(*context.keys())

# filename = "wf_image_processing_bad_ref.cwl"
# test_load_process(test_data_dir, filename, recursive=True)

filename = "workflow5.cwl"
context = {}
test_load_process(test_data_dir, filename, recursive=True, context = context)
print(*context.keys())
