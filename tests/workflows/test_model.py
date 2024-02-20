from polus.pipelines.workflows.model import Parameter
from polus.pipelines.workflows.model import CWLType, CWLArray, CWLBasicTypeEnum, CWLBasicType

def test_parameter_cwl_base_type():
    param_name = "input_string"
    type = CWLBasicType(type=CWLBasicTypeEnum.STRING)
    dict = {"id": param_name, "type": type}
    param = Parameter(**dict)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == type


def test_parameter_cwl_complex_type():
    param_name = "input_array_string"
    type = CWLArray(items=CWLBasicType(type=CWLBasicTypeEnum.STRING))
    param = Parameter(id=param_name, type=type)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == type

def test_parameter_cwl_complex_type1():
    param_name = "input_array_string"
    type = CWLArray(items=CWLBasicType(type=CWLBasicTypeEnum.STRING))
    dict = {'type':'array' , 'items': 'string'}
    type = CWLArray(**dict)
    param = Parameter(id=param_name, type=type)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == type

def test_parameter_cwl_complex_type2():
    param_name = "input_array_string"
    dict = {'items': 'string'}
    type = CWLArray(**dict)
    dict = {"id": param_name, "type": type.model_dump()}
    param = Parameter(**dict)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == type

def test_parameter_raw_type():
    param_name = "input1"
    type = "string"
    param_type = CWLBasicType(type=CWLBasicTypeEnum.STRING)
    dict = {"id": param_name, "type": type}
    param = Parameter(**dict)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == param_type

def test_parameter_serialization():
    param_name = "input1"
    type = CWLBasicType(type=CWLBasicTypeEnum.STRING)
    type_dict_out = 'string'

    # raw data
    dict = {"id": param_name, "type": type}

    # create model and serialize
    param = Parameter(**dict)
    dict_out = param.model_dump()

    # id is unchanged
    assert dict_out["id"] == param_name
    # type is serialized to its raw representation
    assert dict_out["type"] == type_dict_out 
    # optional not serialized
    assert not "optional" in dict_out