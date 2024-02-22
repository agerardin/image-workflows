"""Test building parameters of various types."""

from polus.pipelines.workflows.model import Parameter
from polus.pipelines.workflows.model import (
    CWLArray, CWLBasicTypeEnum, CWLBasicType
)


def test_parameter_cwl_complex_type_model():
    """Test creating a parameter of type array from CWLArray instance.
    
    The CWL Array is also created from a instance.
    """
    param_name = "input_array_string"
    type = CWLArray(items=CWLBasicType(type=CWLBasicTypeEnum.STRING))
    param = Parameter(id=param_name, type=type)

    assert param.id == param_name
    assert param.optional == False
    assert param.type == type


def test_parameter_cwl_complex_type_raw():
    """Test creating a parameter of type array from CWLArray instance.
    
    The array is created from a dict.
    """
    param_name = "input_array_string"
    dict = {'type':'array' , 'items': 'string'}
    type = CWLArray(**dict) # build array from dcit
    param = Parameter(id=param_name, type=type)
    
    param_type = CWLArray(items=CWLBasicType(type=CWLBasicTypeEnum.STRING))
    assert param.id == param_name
    assert param.optional == False
    assert param.type == param_type


def test_parameter_cwl_complex_type_dump_model():
    """Test creating a parameter of type array from dict."""
    param_name = "input_array_string"
    dict = {'items': 'string'} # type is unecessary
    type = CWLArray(**dict)
    
    # use model dump to serialize array
    dict = {"id": param_name, "type": type.model_dump()}
    param = Parameter(**dict)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == type


def test_parameter_cwl_base_type():
    "Test creating a param of type string."
    param_name = "input_string"
    type = CWLBasicType(type=CWLBasicTypeEnum.STRING)
    dict = {"id": param_name, "type": type}
    param = Parameter(**dict)

    assert param.id == param_name
    assert param.optional == False
    assert param.type == type


def test_parameter_cwl_base_type_raw():
    "Test creating a param of type string."
    param_name = "input1"
    type = "string"
    dict = {"id": param_name, "type": type}
    param = Parameter(**dict)

    param_type = CWLBasicType(type=CWLBasicTypeEnum.STRING)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == param_type


def test_parameter_serialization():
    """Test the serialization of a parameter."""
    param_name = "input1"
    type = CWLBasicType(type=CWLBasicTypeEnum.STRING)
    # raw data
    dict = {"id": param_name, "type": type}
    # create model and serialize
    param = Parameter(**dict)
    dict_out = param.model_dump()

    # id is unchanged
    assert dict_out["id"] == param_name
    # type is serialized to its raw representation
    type_dict_out = 'string'
    assert dict_out["type"] == type_dict_out 
    # optional not serialized
    assert not "optional" in dict_out