# from typing import Annotated, Any, Union, get_args
# from pydantic import (
#     BaseModel, ConfigDict, Field, PrivateAttr, ValidationError,
#     computed_field, validator, WrapSerializer, field_serializer
# )
# from enum import Enum
# from pathlib import Path

# class CWLTypeEnum(str, Enum):
#     NULL = "null"
#     BOOLEAN = "boolean"
#     INT = "int"
#     LONG = "long"
#     FLOAT = "float"
#     DOUBLE = "double"
#     STRING = "string"
#     FILE = "File"
#     DIRECTORY = "Directory"

#     def isValidType(self, type):
#         if self == CWLBaseType.STRING:
#             return isinstance(type, str)
#         elif self == CWLBaseType.INT or self == CWLBaseType.LONG:
#             return isinstance(type, int)
#         elif self == CWLBaseType.FLOAT or self == CWLBaseType.DOUBLE:
#             return isinstance(type, float)
#         elif self == CWLBaseType.FILE or self == CWLBaseType.DIRECTORY:
#             return isinstance(type,Path)

# class CWLBaseType(BaseModel):
#     type: CWLTypeEnum

# class CWLArray(BaseModel):
#     items: 'CWLType'

# class _CWLType(BaseModel):
#     id: Union[CWLBaseType, CWLArray]

# def wrap_type(value: Any, handler) -> str:
#     return value.id

# CWLType = Annotated[_CWLType, WrapSerializer(wrap_type)]

# _type1 = {"id":"string"}
# type1 = CWLType(**_type1)

