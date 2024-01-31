from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum

class CwlType(Enum):
    CWL_STRING = 1

class CwlFormat:
    pass

class Process:
    def __init__(self):
        self._ios = {}

    def __setattr__(self, name, value):
        # protected input/outputs
        if name == "_ios":
            if self._ios is None:
                super().__setattr__(name, value)
            else:
                raise Exception("Cannot set protected _ios")
        # cwl inputs are proxied for type checking
        elif self.is_allowable_cwl(value):
            value = ProcessIO(value)
            # if name exists retrieve it and check compatibility
            # create a proxy object
            pass
            # add to dictionary
            self._ios[name] = value
            super().__setattr__(name, value)
        # NOTE decision : every other attribute assignment should fail
        else:
            raise Exception(f"{name} , {value}")

    def validate(self):
        print("check this step is valid.")

    def is_allowable_cwl(self, value):
        return _is_allowable_cwl(value)

    def __getattr__(self,name):
        print(f"cannot find attribute : {name}")
        return None

def _is_allowable_cwl(value):
        return isinstance(value, str)

def _convert_to_cwl_type(value):
    if isinstance(value, str):
        return CwlType.CWL_STRING
    else:
        raise Exception("invalid cwl type")

@dataclass
class ProcessIO:
    value: Any
    type: Optional[CwlType] = None
    process: Optional[Process] = None
    format: Optional[CwlFormat] = None

    def __post_init__(self):
        # if no type is provided, try to get from the value
        if type is None:
            if not _is_allowable_cwl(self.value):
                raise Exception(f"invalid value type {self.value} : {self.value.__class__}")


class Step(Process):
    pass


step1 = Step()
step1.name = "step1"

print(step1.name)
step1.validate()

print(step1.hfd)

step2 = Step()
step2.name = "step2"
# step2.id = 43  #this would fail as not in the allowed types
