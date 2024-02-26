from typing import Annotated
from pydantic import (
    BaseModel, BeforeValidator, ConfigDict, Field, SerializerFunctionWrapHandler, ValidationError,
    computed_field, WrapSerializer, field_serializer
)
from pydantic.functional_validators import field_validator
from pathlib import Path
import yaml
from typing import Any
from rich import print
from enum import Enum


class CWLBasicTypeEnum(Enum):
    """CWL basic types."""

    NULL = "null"
    BOOLEAN = "boolean"
    INT = "int"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    FILE = "File"
    DIRECTORY = "Directory"

    def is_valid_type(self, value: Any):
        """Check if the python variable type can be assigned to this cwl type."""
        if self == CWLBasicTypeEnum.STRING:
            return isinstance(value, str)
        elif self == CWLBasicTypeEnum.INT or self == CWLBasicTypeEnum.LONG:
            return isinstance(value, int)
        elif self == CWLBasicTypeEnum.FLOAT or self == CWLBasicTypeEnum.DOUBLE:
            return isinstance(value, float)
        elif self == CWLBasicTypeEnum.FILE or self == CWLBasicTypeEnum.DIRECTORY:
            return isinstance(value,Path)
        elif self == CWLBasicTypeEnum.BOOLEAN:
            return isinstance(value, bool)
        # default
        return False

class CWLTypes_(BaseModel):
    """Base Model for all CWL Types."""
    pass

def serialize_type(type: Any, nxt: SerializerFunctionWrapHandler = None) -> Any:
    """Serialize CWLTypes based on actual type."""
    if isinstance(type, CWLBasicTypes):
        return type.type.value
    else:
        return {"type": "array", "items": serialize_type(type.items)}

def processType(type):
    """Factory for the concrete type."""
    if isinstance(type, str):
        return CWLBasicTypes(type=type)
    else:
        return CWLArray(**type)

# Representation of any cwltypes.
CWLTypes = Annotated[CWLTypes_, BeforeValidator(processType), WrapSerializer(serialize_type)]

class CWLBasicTypes(CWLTypes_):
    """Model that wraps an enum representing the basic types."""
    type: CWLBasicTypeEnum

    def is_valid_type(self, value):
        """Check if the given value is represented by this type."""
        return self.type.is_valid_type(value)

    
class CWLArray(CWLTypes_):
    """Model that represents a CWL Array"""
    type: str = 'array'
    items: CWLTypes

    def is_valid_type(self, value : Any):
        """Check the python variable type can be assigned to this cwl type."""
        if not isinstance(value, list):
            return False
        # TODO we only check the first value
        # should we check all values?
        return self.items.is_valid_type(value[0])


class WorklfowInput(BaseModel):
    type: CWLTypes


type_dict = {"type":"string"}
input = WorklfowInput(**type_dict)
print(input)
print(input.model_dump())

assert input.model_dump() == {'type': 'string'}

assert input.type.is_valid_type("ok")

array_dict = { "type": {"type": "array", "items": "string"}}
input = WorklfowInput(**array_dict)
print(input)
print(input.model_dump())

assert input.type.is_valid_type(["ok"])

assert input.model_dump() == {'type': {'type': 'array', 'items': 'string'}}

nested_array_dict = { "type": 
                        {
                        "type": "array", 
                        "items": 
                            {
                            "type": "array",
                            "items": "string"
                            }
                        }
                    }
input = WorklfowInput(**nested_array_dict)
print(input)
print(input.model_dump())

assert input.model_dump() == {'type': {'type': 'array', 'items': {'type': 'array', 'items': 'string'}}}

assert input.type.is_valid_type([["ok"]])
assert not input.type.is_valid_type([[4]])
assert not input.type.is_valid_type([4])
assert not input.type.is_valid_type([[["ok"]]])

assert input.type.is_valid_type([["ok"],[4]])


array_dict = { "type": {"type": "array", "items": "File"}}
input = WorklfowInput(**array_dict)
print(input)
print(input.model_dump())

assert input.type.is_valid_type([Path("path/to/file")])