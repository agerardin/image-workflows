import yaml
from pathlib import Path
import cwl_utils.parser as cwl_parser
from model import CommandLineTool
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

echo_string_file = Path("tests/echo_string.cwl")
echo_string = CommandLineTool.load(echo_string_file)