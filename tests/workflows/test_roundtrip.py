import pytest

import yaml
from pathlib import Path
import cwl_utils.parser as cwl_parser
from polus.pipelines.workflows import (
    CommandLineTool, Workflow,
    StepBuilder, WorkflowBuilder
)
import logging
from rich import print
import filecmp
import tempfile
import shutil

logger = logging.getLogger()

@pytest.mark.skip(reason="not implemented")
def test_parsing_doc_with_special_character_string():
    """Test that docstring with |- are taken care of."""
    NotImplemented

@pytest.mark.parametrize("filename", ["echo_string.cwl"])
def test_clt_roundtrip(test_data_dir: Path, tmp_dir: Path, filename):
    """Test model roundtrip to check there is no loss of information
    when serializing our model.
    ."""
    cwl_file = test_data_dir / filename

    # standardized ref file from cwlparser
    ref_filepath = Path(tmp_dir) / f"ref_{filename}.cwl"
    ref_model = cwl_parser.load_document_by_uri(cwl_file)
    serialized_ref_model = cwl_parser.save(ref_model)
    with ref_filepath.open("w", encoding="utf-8") as ref_file:
        ref_file.write(yaml.dump(serialized_ref_model))

    # read cwl and dump model
    new_model = CommandLineTool.load(cwl_file)
    new_model_file = new_model.save()
    roundtrip_model = cwl_parser.load_document_by_uri(new_model_file)
    serialized_roundtrip_model = cwl_parser.save(roundtrip_model)
    
    # write model
    roundtrip_filepath = Path(tmp_dir) / "round_trip_echo_string.cwl"
    with roundtrip_filepath.open("w", encoding="utf-8") as roundtrip_file:
        roundtrip_file.write(yaml.dump(serialized_roundtrip_model))
    
    # make sure ref and dumped model are identical
    assert filecmp.cmp(ref_filepath,roundtrip_filepath, shallow=False)

    shutil.rmtree(tmp_dir)
