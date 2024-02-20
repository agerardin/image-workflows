from pydantic import BaseModel
from rich import print

class Child(BaseModel):
    age: int

class Parent(BaseModel):
    children: list[Child]

def test_create_nested_model():
    child1 = Child(age = 4)
    parent1 = Parent(children=[child1])
    print(parent1)

test_create_nested_model()