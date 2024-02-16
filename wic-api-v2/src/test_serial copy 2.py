from datetime import datetime, timezone
from typing import Any, Dict

from typing_extensions import Annotated

from pydantic import BaseModel, WrapSerializer, Field

class WorkflowStepOutput(BaseModel):
    type: str = None
    value: str = None
    id: str = Field(default = "id")

def convert_to_string(value: Any, handler) -> str:
    return value.id

WorkflowOutputId = Annotated[WorkflowStepOutput, WrapSerializer(convert_to_string)]

class WorkflowStep(BaseModel):
    out: list[WorkflowOutputId]

dt = WorkflowStepOutput(
    type='string', value='3',id="id2"
)
dt2 = WorkflowStepOutput(
    type='string', value='hello',id='id3'
)

dt3 = WorkflowStepOutput()

event = WorkflowStep(out=[dt,dt2,dt3])
print(event.model_dump())