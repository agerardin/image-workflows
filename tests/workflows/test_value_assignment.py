from typing import Any
import pytest
from polus.pipelines.workflows.model import AssignableWorkflowStepInput, CWLBasicType, CWLBasicTypeEnum
from pathlib import Path

@pytest.fixture()
def default_input_model(
    test_data_dir: Path,
    request: pytest.FixtureRequest
    ) -> dict[Any, Any] :
    """Build a template AssignableWorkflowStepInput."""
    input = AssignableWorkflowStepInput(id="test_input",
                                       source="test_source",
                                       type="string",
                                       optional=True,
                                       step_id="test_step_id"
    )
    return input.model_dump()


def test_assign_int(default_input_model: dict[Any, Any]):
    """"Test we can only assign an int."""
    type_dict = {"type":"int"}
    input_model = {**default_input_model, **type_dict, "optional":True}
    input = AssignableWorkflowStepInput(**input_model)

    # TODO CHECK optional is not serialize. 
    # How can we still dump the raw model?
    # TODO review serialization to make this possible
    # assert input.type.model_dump() == {'type': 'int'}
    # TODO move to model test afterwards
    assert input.type == CWLBasicType(type=CWLBasicTypeEnum.INT)

    assert input.type.is_valid_type(4), f"Was expecting a int, got {input.type}"
    assert not input.type.is_valid_type("ok")


def test_assign_string(default_input_model: dict[Any, Any]):
    """"Test we can only assign an string."""
    type_dict = {"type":"string"}
    input_model = {**default_input_model, **type_dict, "optional": True}
    input = AssignableWorkflowStepInput(**input_model)

    assert input.type.is_valid_type("ok"), f"Was expecting a int, got {input.type}"
    assert not input.type.is_valid_type(4)

def test_assign_array_of_strings(default_input_model: dict[Any, Any]):
    """"Test we can only assign an array of strings."""
    type_dict = { "type": {"type": "array", "items": "string"}}
    input_model = {**default_input_model, **type_dict, "optional": True}
    input = AssignableWorkflowStepInput(**input_model)

    # assert input.model_dump() == {'type': {'type': 'array', 'items': 'string'}}

    assert input.type.is_valid_type(["ok"])
    assert input.type.is_valid_type(["ok1","ok2"])
    assert not input.type.is_valid_type(["ok", 4]) #cannot mix strings and ints


def test_assign_array_of_files(default_input_model: dict[Any, Any]):
    """"Test we can only assign an array of paths."""
    type_dict = { "type": {"type": "array", "items": "File"}}
    input_model = {**default_input_model, **type_dict, "optional": True}
    input = AssignableWorkflowStepInput(**input_model)

    assert input.type.is_valid_type(
        [Path("path/to/file1", Path("path/to/file2"))]
        )
    

def test_assign_nested_array(default_input_model: dict[Any, Any]):
    """"Test we can only assign a nested array."""
    type_dict = { "type": 
                    {
                    "type": "array", 
                    "items": 
                        {
                        "type": "array",
                        "items": "string"
                        }
                    }
                }
    input_model = {**default_input_model, **type_dict, "optional": True}
    input = AssignableWorkflowStepInput(**input_model)

    # assert input.model_dump() == {'type': {'type': 'array', 'items': {'type': 'array', 'items': 'string'}}}

    assert input.type.is_valid_type([["ok"]]) # nested array of strings ok
    assert not input.type.is_valid_type([[4]]) # nested array of int not ok
    assert not input.type.is_valid_type([4]) # simple array not ok
    assert not input.type.is_valid_type([[["ok"]]]) # deeper array nesting not ok
    assert not input.type.is_valid_type([["ok"],[4]]) # cannot mix and match types.
