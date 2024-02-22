from typing import Optional
from pydantic import BaseModel, ConfigDict, model_serializer
from rich import print

class Process(BaseModel):
    """Process is the base class for Workflows,CommandLineTools
    (and also Expression Tools and Operations).

    see (https://www.commonwl.org/user_guide/introduction/basic-concepts.html)
    """
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    requirements: Optional[list[dict[str, object]]] = []    

    @model_serializer(mode="wrap", when_used="always")
    def serialize_model(self, next):
        serialization = next(self)
        if not self.requirements:
          serialization.pop("requirements")
        return serialization

dict = {"id":"id1"}
p = Process(**dict)
m = p.model_dump()

print(m)
