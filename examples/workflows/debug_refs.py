"""Model for the workflow builder DSL."""

import abc
from typing import Annotated, Union, get_args
from pydantic import (
    BaseModel, BeforeValidator, ConfigDict, 
    SerializerFunctionWrapHandler, UrlConstraints, WrapSerializer, 
    Field, computed_field, field_serializer,
    model_serializer
)
from pydantic.functional_validators import (
    AfterValidator, field_validator
)
import cwl_utils.parser as cwl_parser
from pydantic_core import Url
import pydantic_core
from schema_salad.exceptions import ValidationException as CwlParserException
from urllib.parse import urlparse, unquote
from pathlib import Path
import yaml
from typing import Optional, Any
from rich import print
from enum import Enum

FileUrl = Annotated[
    Url, UrlConstraints(allowed_schemes=["file"])
]

print(get_args(FileUrl))

check = get_args(FileUrl)[0]

print(check)