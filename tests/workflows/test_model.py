from polus.pipelines.workflows.model import CWLTypes, CWLArray, Parameter

def test_parameter_cwl_base_type():
    param_name = "input_string"
    type = CWLTypes.STRING
    dict = {"id": param_name, "type": type}
    param = Parameter(**dict)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == type

def test_parameter_cwl_base_type_2():
    """Using model_validate instead"""
    param_name = "input_string"
    type = CWLTypes.STRING
    dict = {"id": param_name, "type": type}
    param = Parameter.model_validate(dict)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == type

def test_parameter_cwl_complex_type():
    param_name = "input_array_string"
    type_ = CWLArray(items=CWLTypes.STRING)

def test_parameter_cwl_complex_type1():
    param_name = "input_array_string"
    dict = {'items': 'string'}
    type_ = CWLArray(**dict)
    param = Parameter(id=param_name, type=type_)
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
    param_type = CWLTypes.STRING
    dict = {"id": param_name, "type": type}
    param = Parameter(**dict)
    assert param.id == param_name
    assert param.optional == False
    assert param.type == param_type

def test_parameter_serialization():
    param_name = "input1"
    type = CWLTypes.STRING
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