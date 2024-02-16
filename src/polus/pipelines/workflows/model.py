from typing import Annotated, Union
from pydantic import (
    BaseModel, ConfigDict, Field, PrivateAttr, ValidationError,
    computed_field, validator, WrapSerializer, field_serializer
)
from pydantic.functional_validators import AfterValidator, field_validator
import cwl_utils.parser as cwl_parser
from pathlib import Path
from yaml import safe_load, dump
import yaml
from pydantic.dataclasses import dataclass
from typing import NewType, Optional, Any
from rich import print
from urllib.parse import unquote, urlparse
from enum import Enum


class CWLTypes(str, Enum):
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


# TODO FIX 
# per https://www.commonwl.org/v1.2/Workflow.html#InputArraySchema
# we can have nested arrays at any level.
# For now we only handle array of base types.
class CWLArray(BaseModel):
    """Array of elements of base types."""

    items: CWLTypes

    #TODO CHECK Python raw type is correct
    def isValidType(self, value : Any):
        """Check the python variable type can be assigned to this cwl type."""
        return isinstance(value, list)


def file_exists(path : Path):
    """Check we have a file a disk."""
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError
    if not path.is_file():
        raise NotAFileError(path)
    return path


class NotAFileError(Exception):
    """Raised if path is not a file."""
    def __init__(self, path):
        super().__init__(f"{path} is not a file.")


class IncompatibleTypeError(Exception):
    """Raised if types are incompatible."""
    def __init__(self, type1, type2):
        super().__init__(f"{type1} != {type2}")


class IncompatibleValueError(Exception):
    """Raised if value cannot be assigned to a type."""
    def __init__(self, io_id, type, value):
        super().__init__(f"Cannot assign {value} to {io_id} of type {type}") 


def validProcessId(id):
    """Check the process id (which is an uri) points to an existing file on disk."""
    # TODO need to figure out how to deal with from_builder=True
    # where file is not yet created.
    # try:
    #     path = Path(unquote(urlparse(id).path))
    #     path = file_exists(path)
    # except Exception:
    #     print(id)
    #     raise Exception
    # assert path.suffix == ".cwl"
    return id
    

"""
ProcessId needs to points to an existing file on disk
in order to be pulled in a Workflow definition.
However, when we first instantiated a newly buildworkfow, the 
files does not yet exists on disk.
"""
ProcessId = Annotated[str, AfterValidator(validProcessId)]

class ProcessRequirement(BaseModel):
    """Base class for all process requirements."""
    model_config = ConfigDict(populate_by_name=True)

class SubworkflowFeatureRequirement(ProcessRequirement):
    """Needed if a Workflow references other Workflows."""
    class_: Optional[str] = Field("SubworkflowFeatureRequirement", alias='class')

class SoftwareRequirement(ProcessRequirement):
    """Software requirements. """
    NotImplemented

class DockerRequirement(ProcessRequirement):
    """Docker requirements. """
    NotImplemented 

# TODO Probably unecessary
class InputBinding(BaseModel):
    """Base class for any Input Binding."""
    pass

# TODO CHANGE name. For now stick to cwl_parser naming
# but should be CLTInputBinding
class CommandLineBinding(InputBinding, extra='ignore'):
    """Describe how to translate the input parameter to a
    program argument.
    """
    # TODO Capture other missing attributes.
    position: Optional[int] = None

# TODO CHANGE name. For now stick to cwl_parser naming
# but should be CLTOutputBinding
class CommandOutputBinding(BaseModel):
    """Describe how to translate the wrapped program result
    into a an output parameter.
    """
    glob: Optional[str] = None
    loadContents: Optional[bool] = None
    outputEval: Optional[str] = None

# TODO CHECK maybe add checks for ParameterIds
ParameterId = Annotated[str,[]]

class Parameter(BaseModel):
    """
    Base representation of any parameters.
    Every parameter must have an id and a type.
    """
    id: ParameterId
    type: Union[CWLTypes,CWLArray]

    # TODO TEST and FIX.
    # This needs to be recursively parsing nested structures.
    @field_validator("type", mode="before")
    @classmethod
    def transform_type(cls, type: Any) -> Union[CWLTypes,CWLArray]:
        """Ingest any python type an transform it into a valid CWLType."""
        if isinstance(type, dict):
            return CWLArray(**type)
        if isinstance(type, list):
            if type[0] == 'null':
                # TODO CHECK what to do with unset optional
                return
            else:
                # TODO CHECK can we get other kind of list?
                raise NotImplementedError
        return CWLTypes(type)

    @field_serializer('type', when_used='always')
    def serialize_type(type: Union[CWLTypes,CWLArray]):
        """Define rules to serialize parameter types."""
        if isinstance(type, CWLTypes):
            serialized_type = type.value
        elif isinstance(type, CWLArray):
            # TODO maybe switch to standard form instead
            serialized_type = f"{type.items.value}[]"
        else:
            raise NotImplementedError(f"No support for type : {type}")
        return serialized_type

class InputParameter(Parameter):
    """Base class of any input parameter."""
    pass

class OutputParameter(Parameter):
    """Base class of any input parameter."""
    pass


class WorkflowInputParameter(InputParameter):
    """Workflow input parameters define how what inputs
    to provide to execute a workflow."""
    # TODO CHECK for now, rely on step logic to generate config
    #  we may revisit later
    # value:Optional[Any] = Field(None, exclude=True)
    pass

class WorkflowOutputParameter(OutputParameter):
    """Workflow output parameters define how to collect
    the outputs of a workflow.
    Args:
    - outputSource: ref to the WorkflowStepOutput 
    this workflow output is linked to.
    """
    # TODO CHECK maybe add additional constraints?
    outputSource: str

class CommandInputParameter(InputParameter):
    """Command Line Tool input parameter.
    """
    inputBinding: Optional[CommandLineBinding] = None


class CommandOutputParameter(OutputParameter):
    """Command Line Tool output parameter.
    """
    outputBinding: Optional[CommandOutputBinding] = None

# TODO CHECK if we need extra validation.
StepInputId = Annotated[str,[]]

class WorkflowStepInput(BaseModel):
    """A WorkflowStepInput describes how to provide
    an input to a workflow step.

    It provides a ref to a workflow input or another step output.
    """
    id: StepInputId
    source: str #TODO CHECK add typing for extra check if necessary.

class AssignableWorkflowStepInput(WorkflowStepInput):
    """This a special kind of WorkflowStepInput that can
    be dynamically assign a value or link to another workflow input 
    or step output.
    """
    type: Union[CWLTypes,CWLArray] = Field(exclude=True)
    value: None
    step_id: str = None

    # TODO we also do the type checking here because type is a union
    # transform type to a base model so we can factor this code everywhere.
    @field_validator("type", mode="before")
    @classmethod
    def transform_type(cls, type: Any) -> Union[CWLTypes,CWLArray]:
        if isinstance(type, dict):
            return CWLArray(**type)
        if isinstance(type, list):
            if type[0] == 'null':
                # TODO CHECK what to do with unset optional
                return
            else:
                raise NotImplementedError
        return CWLTypes(type)

    @field_serializer('type', when_used='always')
    def serialize_type(type: Union[CWLTypes,CWLArray]):
        if isinstance(type, CWLTypes):
            serialized_type = type.value
        elif isinstance(type, CWLArray):
            serialized_type = f"{type.items.value}[]"
        else:
            raise NotImplementedError
        return serialized_type

    # TODO CHECK we could use pydantic model instead
    def set_value(self, value: Any):
        """Assign a value to this step input or link it to another
        step output.
        """
        if isinstance(value, AssignableWorkflowStepOutput):
            if(self.type != value.type):
                raise IncompatibleTypeError(self.type, value.type)
            # TODO create a function for that
            self.source = value.step_id + "/" + value.id
        elif value is not None:
            if not self.type.isValidType(value):
                raise IncompatibleValueError(self.id, self.type, value)
        else:
            # TODO remove when poc is completed.
            raise NotImplementedError("this case is not properly handled.")
        self.value = value

class WorkflowStepOutput(BaseModel):
    """WorkflowStepOuput define the name of a step output
    that can be used to reference it in another step input or a workflow output.
    """
    id: str

def convert_to_string(value: Any, handler) -> str:
    return value.id

"""WorkflowStepOutput are represented as string so we wrap the pydantic model to hide
from the callers.
"""
WorkflowStepOutputId = Annotated[WorkflowStepOutput, WrapSerializer(convert_to_string)]

class AssignableWorkflowStepOutput(WorkflowStepOutput):
    """This a special kind of WorkflowStepOutput that can
    be dynamically link to another step input.
    """
    type: Union[CWLTypes,CWLArray] = Field(exclude=True)
    value: str = None
    step_id: str = None

    # TODO third time we need to do the same validation.
    # Need to factor that code otherwise bugs will creep in.
    @field_validator("type", mode="before")
    @classmethod
    def transform_type(cls, type: Any) -> Union[CWLTypes,CWLArray]:
        if isinstance(type, dict):
            return CWLArray(**type)
        if isinstance(type, list):
            if type[0] == 'null':
                # TODO CHECK what to do with unset optional
                return
            else:
                raise NotImplementedError
        return CWLTypes(type)

    @field_serializer('type', when_used='always')
    def serialize_type(type: Union[CWLTypes,CWLArray]):
        if isinstance(type, CWLTypes):
            serialized_type = type.value
        elif isinstance(type, CWLArray):
            serialized_type = f"{type.items.value}[]"
        else:
            raise NotImplementedError
        return serialized_type

WorkflowStepId = Annotated[str,[]]

class WorkflowStep(BaseModel):
    """Capture a workflow step.
    
    A workflow step has an id so it can be referenced by other steps,
    or workflow ios.
    It has a list of inputs whose ids correspond to the process input ids they 
    are wrapping and describe to which workflow input/step output the connect.
    It has a list of outputs whose ids correspond to the process output ids they
    are wrapping and describe to  which workflow output they connect.
    """

    # needed because of the reserved `in` keyword used in the model.
    model_config = ConfigDict(populate_by_name=True)
    
    id: WorkflowStepId
    run: str
    in_: list[WorkflowStepInput] = Field(..., alias='in')
    out: list[WorkflowStepOutputId]
    # TODO CHECK if we can type it to StepInputId
    scatter: Optional[list[str]] = Field(None) # ref to scatter inputs
    when: Optional[str] = Field(None) # ref to conditional execution clauses

    # TODO CHECK we may remove that later
    from_builder: Optional[bool] = Field(False, exclude=True)


    @field_validator("out", mode="before")
    # type: ignore
    @classmethod
    def transform_workflow_step_output(cls, out) -> Any:  # pylint: disable=no-self-argument
        """Return name of input from InputParameter.id."""
        res = [{"id": wf_step_output} for wf_step_output in out]
        return res
    
    # TODO this could be move to the CWLModel pydantic model once we have it.
    def promote_cwl_type(self, type: CWLTypes):
        """When scattering over some inputs, we will provide arrays of value of the
        original types.
        """
        if isinstance(type, CWLArray):
            #TODO FIX
            raise NotImplementedError("scattering CWLArray is not yet implemented.")
        return {"type": "array", "items": type}
        

    # TODO use pydantic model instead
    def set_mutable_ios(self,
                        inputs: list[dict],
                        outputs: list[dict]):
        """A step can be used as a building block for creating a workflow.
        
        When used as such, we enable step inputs/outputs to be linked with other
        steps or workflows inputs/outputs, or to assign its step some value.
        Links will be used to generate the final workflow definitions.
        Values are captured and can be stored in a config file that can be then 
        submitted along the workflow specification for execution.
        """
        # TODO CHECK For now recreate assignable model.
        # Let's make sure it is the best solution.
        inputs = {input["id"]:input for input in inputs}
        outputs = {output["id"]:output for output in outputs}

        assignable_ins = []
        _inputs = {}
        for step_in in self.in_:
            process_input = inputs[step_in.id]
            # TODO change when we have a model
            in_type = process_input["type"]
            if self.scatter:
                if step_in.id in self.scatter:
                    in_type = self.promote_cwl_type(in_type)

            print(f"!!!!!! {in_type}")
            values = step_in.model_dump()
            assignable_in = AssignableWorkflowStepInput(
                **values,
                value=None,
                type=in_type,
                step_id=self.id
                )
            assignable_ins.append(assignable_in)
            _inputs[step_in.id] = assignable_in

        self.in_ = assignable_ins
        self._inputs = _inputs

        assignable_outs = []
        _outputs = {}
        for step_out in self.out:
            process_output = outputs[step_out.id]
            # TODO change when have a model
            out_type = process_output["type"]
            if self.scatter:
                out_type = self.promote_cwl_type(out_type)
            values = step_out.model_dump()
            assignable_out = AssignableWorkflowStepOutput(
                **values, type=out_type, step_id=self.id
                )
            assignable_outs.append(assignable_out)
            _outputs[step_out.id] = assignable_out
        self.out = assignable_outs
        self._outputs = _outputs

    def __setattr__(self, name: str, value: Any) -> None:
        """This is enabling assignment in our python DSL."""
        if name in [
                    "in_",
                    "_inputs",
                    "out",
                    "_outputs"
                    ]:
            return super().__setattr__(name, value)
        if(self._inputs and name in self._inputs):
            input = self._inputs[name]
            input.set_value(value)
            print(input)
        elif(self._outputs and name in self._outputs):
            output = self._outputs[name]
            output.set_value(value)
        else:
            raise AttributeError(f"undefined attribute {name}")

    def __getattr__(self, name: str) -> Any:
        """This is enabling assignment in our python DSL."""
        # TODO CHECK Note there is an ordering issues here
        # if we ever need to check inputs because 
        # a input and an output can have the same name!
        # NOTE we could disambiguate in from out if necessary
        # NOTE similarly, we could create unique step name if necessary.
        # (in case the same step is repeated n times).
        if(self._outputs and name in self._outputs):
            print(f"output  found {name}")
            return self._outputs[name]
        
        # TODO CHECK return defensive copy / read-only?
        # we can use inputs to check property of the workflow
        if(self._inputs and name in self._inputs):
            print(f"input  found {name}")
            return self._inputs[name]

    def save_config(self, path = Path()) -> Path:
        """Save the workflow configuration."""
        config = {input.id: input.value for input in self.in_ if input.value}
        
        #TODO same code as process.save() so factor
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError()
        if not path.is_dir():
            # TODO create exception for this?
            # TODO fallback (like checking parent and using it?)
            raise Exception(f"{path} is not a directory.")

        file_path = path / (self.id + ".yaml")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(dump(config))
            return file_path 
    

class Process(BaseModel):
    """Process is the base class for Workflows,CommandLineTools
    (and also Expression Tools and Operations).

    see (https://www.commonwl.org/user_guide/introduction/basic-concepts.html)
    """
    model_config = ConfigDict(populate_by_name=True)
    
    id: ProcessId

    # TODO can class attribute be declared there and overidden in subclasses?

    @computed_field
    @property
    def name(self) -> str:
        """Generate a name from the id for convenience purpose."""
        # TODO CHECK this works for any allowable CLT
        name = Path(self.id).stem
        return name
    
    def save(self, path = Path()) -> Path:
        """
        Create a cwl file.
        Process computed name is ignored.

        Args:
            - path : the directories in which in to create the file.
        """
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError()
        if not path.is_dir():
            # TODO create exception for this?
            # TODO fallback (like checking parent and using it?)
            raise Exception(f"{path} is not a directory.")

        file_path = path / (self.name + ".cwl")
        serialized_process = self.model_dump(by_alias=True, exclude={'name'}, exclude_none=True)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(dump(serialized_process))
            return file_path 

    # TODO CHECK can we have equivalent of virtual methods in python?
    # load() should be defined by subclass but declared here.

class Workflow(Process):
    """Represents a CWL Workflow.
    
    Workflows are represented by inputs outputs and a list of steps.
    """

    inputs: list[WorkflowInputParameter]
    outputs: list[WorkflowOutputParameter]
    steps: list[WorkflowStep]
    # TODO CHECK which can be factor in process?
    requirements: Optional[list[dict[str, object]]] = []
    from_builder: Optional[bool] = Field(False, exclude=True)
    # TODO CHECK if we can factor in process
    class_: Optional[str] = Field(alias='class', default='Workflow')
    
    # TODO extract version from the definition instead.
    # decide if we want to accomodate different versions
    # or reject <1.2 altogether
    cwlVersion: str = "v1.2"

    # TODO CHECK should factor that too
    @property
    def _inputs(self) -> dict[ParameterId, WorkflowInputParameter]:
        """internal index to retrieve inputs efficiently."""
        return {input.id: input for input in self.inputs}

    # TODO CHECK should factor that too
    @property
    def _outputs(self) -> dict[ParameterId, WorkflowOutputParameter]:
        """internal index to retrieve outputs efficiently."""
        return {output.id: output for output in self.outputs}

    # TODO See comment on CommandLineTool.load
    @classmethod
    def load(cls, clt_file: Path) -> 'Workflow':
        """Load a Workflow from a cwl workflow file.
        
        We use the reference cwl parser to get a standardized description.
        """
        clt_file = file_exists(clt_file)
        cwl_clt = cwl_parser.load_document_by_uri(clt_file)
        # TODO CHECK save rewrite ids and runs ref.
        # Make sure this is not an issue.
        # In particular rewrite runs can be an issue if not managed properly
        # (could have clashing definitions).
        yaml_clt = cwl_parser.save(cwl_clt)
        return cls(**yaml_clt) 

class CommandLineTool(Process):
    """Represent a CommandLineTool.
    """
    model_config = ConfigDict(extra='ignore')
    baseCommand: str
    inputs: list[CommandInputParameter]
    outputs: list[CommandOutputParameter]
    stdout: Optional[str] = None

    # TODO CHECK move those to process most likely
    cwlVersion: Optional[str] = "v1.2"
    class_: Optional[str] = Field(..., alias='class') 
    doc: Optional[str] = ""
    label: Optional[str] = ""

    @property
    def _inputs(self) -> dict[ParameterId, CommandInputParameter]:
        """internal index to retrieve inputs efficiently."""
        return {input.id: input for input in self.inputs}

    @property
    def _outputs(self) -> dict[ParameterId, CommandOutputParameter]:
        """internal index to retrieve outputs efficiently."""
        return {output.id: output for output in self.outputs}

    # TODO either check type is commandLine
    # or allow virtual definition in parent class and implement
    # in each subclass.
    @classmethod
    def load(cls, clt_file: Path) -> 'CommandLineTool':
        """Load a CLT from a cwl clt file.
        
        We use the reference cwl parser to get a standardized description.
        """
        clt_file = file_exists(clt_file)
        cwl_clt = cwl_parser.load_document_by_uri(clt_file)
        yaml_clt = cwl_parser.save(cwl_clt)
        return cls(**yaml_clt) 

class ExpressionTool:
    NotImplemented

class Operation:
    NotImplemented

class StepBuilder():
    """Create a workflow step.
    
    Create a WorkflowStep from a Process.
    For each input/output of the clt, a corresponding step in/out is created.
    """

    def __init__(self, process : Process,
                 scatter : list[str] = None,
                 when: str = None,
                 add_inputs: list[dict] = None,
                 when_input_names: list[str] = None):
        
        # Generate a step id from the clt name
        id = "step_"+ process.name
        run = process.id

        # TODO change. For now set source to "UNSET"
        inputs = [{"id":input.id, "source":"UNSET", "type": input.type}
                  for input in process.inputs]
        outputs = [output.id for output in process.outputs]
        
        # Generate additional inputs.
        # For example,if the conditional clause contains unknown inputs.
        # It could also be to generate fake inputs for wic compatibility.
        # TODO REVISIT that later after some use.        
        _add_inputs_ids = set([input["id"] for input in add_inputs]) if add_inputs else set()

        # input referenced in the when clause may or may not be already declared if the process.
        # If not, user must provide a description of it.
        # TODO we could evaluate the clause rather than having the user declare explicitly.
        if when:
            if not when_input_names:
                raise Exception("You need to specify which inputs are referenced in the when clause.")
            
            _process_inputs_ids = set([input.id for input in process.inputs])
            for when_input_name in when_input_names:
                if not (when_input_name in _process_inputs_ids):
                    if not(when_input_name in _add_inputs_ids):
                        raise Exception("Input in when clause unknown. Please add its declaration to add_inputs arguments.")
        
        if add_inputs:
            # TODO refactor : same model use twice
            inputs = inputs + [{"id":input["id"], "source":"UNSET", "type": input["type"]}
                for input in add_inputs]
            
        self.step = WorkflowStep(
            scatter = scatter,
            when = when,
            id = id,
            run = run,
            in_ = inputs,
            out = outputs,
            from_builder = True,
            )
        
        # TODO update pydantic to consume this model
        # rather than having to generate string, then type?
        # But we have to make sure it works when loading plain cwl files.
        outputs = [{"id":output.id, "type":output.type} for output in process.outputs]

        self.step.set_mutable_ios(inputs, outputs)    


    def __call__(self) -> WorkflowStep:
        """"Returns the fully constructed WorkflowStep."""
        return self.step

class  WorkflowBuilder():
    """Builder for a workflow object.
    
    Enable creating workflow dynamically.
    """
    def __init__(self, id: str, *args: Any, **kwds: Any):
        kwds.setdefault("steps", [])
        # Collect all step inputs and create a workflow input for each
        # Collect all step outputs and create a workflow output for each
        # NOTE For now each output from each step creates an output.
        # TODO Make this optional.
        # TODO We could also reduced workflow outputs to only those 
        # which are not already connected.
        # TODO Similarly we could have an option to hide/rename steps the list 
        # of workflow inputs.
        def generate_workflow_io_id(worklflow_id : str, step_id: str, io_id: str):
            """generate id for workflow ios. Note that ('/') are forbidden."""
            return worklflow_id + "___" + step_id + "___" + io_id

        workflow_inputs = []
        workflow_outputs = []
        requirements = []
        scatterRequirement = False
        subworkflowFeatureRequirement = False
        inlineJavascriptRequirement = False
        for step in kwds.get("steps"):
            # TODO CHECK best way to test a list is not empty?
            if not not step.scatter:
                scatterRequirement = True
            if not not step.when:
                inlineJavascriptRequirement = True
            for input in step.in_:
                if input.source == 'UNSET':
                    # TODO create method, we could also wrap CWLTypes in a pydantic model
                    input_type = input.type
                    input_type = input_type.model_dump() if isinstance(input_type, CWLArray) else input_type.value
                    workflow_input_id = generate_workflow_io_id(id, step.id, input.id)
                    workflow_input = {"id": workflow_input_id,"type":input_type}
                    input.source = workflow_input_id
                    workflow_inputs.append(workflow_input)

            for output in step.out:
                    output_type = output.type
                    output_type = output_type.model_dump() if isinstance(output_type, CWLArray) else output_type.value
                    workflow_output_id = generate_workflow_io_id(id, step.id, output.id)
                    workflow_output = {"id": workflow_output_id,
                                       "type":output_type,
                                       "outputSource": step.id + "/" + output.id
                                       }
                    workflow_outputs.append(workflow_output)

            # TODO That is where a context of loaded CLTs could be helpful.
            # So we don't keep reloading the same models.
            cwl_file = cwl_parser.load_document_by_uri(step.run)
            yaml_cwl = cwl_parser.save(cwl_file)
            if cwl_file.class_ == "CommandLineTool":
                clt = CommandLineTool(**yaml_cwl)
            elif cwl_file.class_ == "Workflow":
                workflow = Workflow(**yaml_cwl)
                subworkflowFeatureRequirement = True
            else:
                raise Exception(f"Invalid Cwl Class : {cwl_file.class_}")

            # TODO CHECK we can probably revisit and do this a bit differently.
            # The CWL standards allow us to do shallow validation.
            # Now we can also recursively check before execution that all connections
            # are indeed valid.
            # At the very least, in the current usage of compute for example, we need 
            # to ship every cwl we are referencing so we will need at a minimum to collect
            # all cwl files beforehand.

            ## TODO That is where a context of loaded CLTs could be helpful.
            ## So we don't keep reloading the same models.

            # Collect types of each CLT inputs referenced.
            # TODO probably should do it anyhow because we could parse
            # non generated steps.
            # Check that generated steps have correct input types?
            # step_types = {}
            # cwl_file = cwl_parser.load_document_by_uri(step.run)
            # yaml_cwl = cwl_parser.save(cwl_file)
            # if cwl_file.class_ == "CommandLineTool":
            #     clt = CommandLineTool(**yaml_cwl)
            #     step_types[step.id] = clt._outputs
            # elif cwl_file.class_ == "Workflow":
            #     workflow = Workflow(**yaml_cwl)
            #     step_types[step.id] = workflow._outputs
            #     kwds.setdefault("requirements", [{"class": "SubworkflowFeatureRequirement"}])
            # else:
            #     raise Exception(f"Invalid Cwl Class : {cwl_file.class_}")

            # # TODO do not hand generate outputSource but create a method to 
            # # encapsulate this
            # for output in step.out:
            #     out_type = f"{step_types[step.id][output.id].type}[]" if step.scatter else step_types[step.id][output.id].type   
            #     workflow_output = {
            #         "id": generate_workflow_io_id(id, step.id, output.id),
            #         "type": out_type,
            #         "outputSource": step.id + "/" + output.id
            #     }
            # worklfow_outputs.append(workflow_output)
        if scatterRequirement:
            # TODO CHECK cwl spec. if multiple inputs, we also need to add a scatter method.
            requirements.append({"class": "ScatterFeatureRequirement"})
        if subworkflowFeatureRequirement:
            requirements.append({"class": "SubworkflowFeatureRequirement"})                
        if inlineJavascriptRequirement:
            requirements.append({"class": "InlineJavascriptRequirement"})

        kwds.setdefault("inputs", workflow_inputs)
        kwds.setdefault("outputs", workflow_outputs)
        kwds.setdefault("requirements", requirements)
        # NOTE for this to work, we would need to serialize to disk
        # TODO CHECK if there is a better way to solve this
        id = (Path() / (id + ".cwl")).resolve().as_uri()
        kwds.setdefault("id", id)

        self.workflow = Workflow(**kwds, from_builder=True)

    def __call__(self) -> Any:
        """Save the workflow description and return the workflow object."""
        # NOTE this could be revisited, but 
        # we need to be able to load the original cwl when creating subworkflows.
        # TODO IMPLEMENT we could also accept a context object containing models of 
        # clts and workflows.
        self.workflow.save()
        return self.workflow

