from typing import Annotated, Union
from pydantic import (
    BaseModel, ConfigDict, Field, SerializerFunctionWrapHandler, ValidationError,
    computed_field, WrapSerializer, field_serializer
)
from pydantic.functional_validators import AfterValidator, field_validator
import cwl_utils.parser as cwl_parser
from pathlib import Path
import yaml
from typing import Optional, Any
from rich import print
from enum import Enum


class CWLTypes(Enum):
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

    def isValidType(self, value: Any):
        """Check the python variable type can be assigned to this cwl type."""
        if self == CWLTypes.STRING:
            return isinstance(value, str)
        elif self == CWLTypes.INT or self == CWLTypes.LONG:
            return isinstance(value, int)
        elif self == CWLTypes.FLOAT or self == CWLTypes.DOUBLE:
            return isinstance(value, float)
        elif self == CWLTypes.FILE or self == CWLTypes.DIRECTORY:
            return isinstance(value,Path)
        elif self == CWLTypes.BOOLEAN:
            return isinstance(value, bool)
        # default
        return False


class CWLTypesUnion(BaseModel):
    pass

class CWLBasicTypes(CWLTypesUnion):
    _type: CWLTypes

class CWLArray(CWLTypesUnion):
    items: CWLTypesUnion

class WorklfowInput:
    type: CWLTypesUnion




