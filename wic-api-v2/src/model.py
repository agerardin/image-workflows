from typing import Union
from pydantic import BaseModel
import cwl_utils.parser as cwl_parser
from pathlib import Path
from yaml import safe_load

class Process(BaseModel):
    pass

class Workflow(Process):
    pass


class CommandLineTool(Process):
    pass

class InputParameter:
    pass


class OutputParameter:
    pass



class WorkflowInputParameter:
    pass

class WorkflowOutputParameter:
    pass

class WorkflowStep:
    pass

class WorkflowStepInput:
    pass

class WorkflowStepOutput:
    pass

class CommandLineBinding:
    pass

class CommandOutputParameter:
    pass 

class ExpressionTool:
    pass

class DockerRequirement:
    pass 

class Operation:
    pass



class ProcessRequirement:
    pass

class SoftwareRequirement:
    pass


cwl_file = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/echo_string.cwl")

with cwl_file.open("r", encoding="utf-8") as file:
    raw_clt = safe_load(file)

# NOTE we use the cwl_parser to standardize the representation
cwl_clt = cwl_parser.load_document_by_uri(cwl_file)
yaml_clt = cwl_parser.save(cwl_clt)


clt = CommandLineTool(**yaml_clt)
print(clt)