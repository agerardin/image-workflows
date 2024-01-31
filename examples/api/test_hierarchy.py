from __future__ import annotations # to allow forward declaration
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum

class CwlType(Enum):
    CWL_STRING = 1

class CwlFormat:
    pass

@dataclass
class ProcessIO:
    value: Optional[Any] = None
    name: Optional[str] = None
    type: Optional[CwlType] = None
    process: Optional[Process] = None
    format: Optional[CwlFormat] = None
    link: Optional[bool] = False
    target: Optional[ProcessIO] = None

    def __post_init__(self):
        # if no type is provided, try to get from the value
        if type is None:
            if not _is_allowable_cwl(self.value):
                raise Exception(f"invalid value type {self.value} : {self.value.__class__}")

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
        elif isinstance(value, ProcessIO):
            print(f"Try to set a new ProcessIO attribute : {name}, {value}")
            if value.link and value.process != self:
                print(f"######## connecting {name} with {value.name}")
                value.target = self
            self._ios[name] = value
            super().__setattr__(name, value)
            

        elif self.is_allowable_cwl(value):
            value = ProcessIO(value)
            # if name exists retrieve it and check compatibility
            # create a proxy object
            pass
            super().__setattr__(name, value)
        # NOTE decision : every other attribute assignment should fail
        else:
            raise Exception(f"Not a cwl type : {name} , {value}")

    def validate(self):
        print("check this step is valid.")

    def is_allowable_cwl(self, value):
        return _is_allowable_cwl(value)

    def __getattr__(self,name):
        print("### THIS SHOULD ONLY BE CALLED THE FIRST TIME")

        if(name == "output" or name == "input"):
            print("top")

        if name != "_ios":
            # we have a forward reference to an new attribute
            # Its definition should be provided on assignment
            link = ProcessIO(process=self,name=name,link=True)
            print(f"create a new ProcessIO attribute {link}")
            self.__setattr__(name,link)
            return self.__getattribute__(name)

            

def _is_allowable_cwl(value):
        return isinstance(value, str)

def _convert_to_cwl_type(value):
    if isinstance(value, str):
        return CwlType.CWL_STRING
    else:
        raise Exception("invalid cwl type")


class Step(Process):

    def __str__(self):
        ios = [item[0] for item in  self._ios.items()]
        return (',').join(ios)


if __name__ == "__main__":
    step1 = Step()
    step1.name1 = "step1"

    print(step1.name)
    step1.validate()

    step2 = Step()
    step2.name2 = "step2"
    # step2.id = 43  #this would fail as not in the allowed types

    step2._ios
    # step1.output # this create a new processIO that is unbound
    # step2.input 
    step2.input = step1.output #NOT ALLOWED

    print(step1)
