from typing import List

from typing_extensions import Annotated

from pydantic import BaseModel, PlainSerializer

class ComplexObject(BaseModel):
    id: str = ""
    type: str = "type"
    value: str = "value"
    

CustomStr = Annotated[
    ComplexObject, PlainSerializer(lambda x: x.id, return_type=str)
]

class StudentModel(BaseModel):
    courses: CustomStr

student = StudentModel(courses=ComplexObject({id:"hello", type:"typeds"}))
print(student.model_dump())
#> {'courses': 'Math Chemistry English'}