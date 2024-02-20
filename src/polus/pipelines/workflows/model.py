from typing import Annotated, Union
from pydantic import (
    BaseModel, ConfigDict, Field, SerializerFunctionWrapHandler, ValidationError,
    computed_field, WrapSerializer, field_serializer
)
from pydantic.functional_validators import AfterValidator, field_validator
import cwl_utils.parser as cwl_parser
from pathlib import Path
import yaml
from typing import Optional, Any
from rich import print
from enum import Enum

class CWLTypes(Enum):
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
        elif self == CWLTypes.BOOLEAN:
            return isinstance(value, bool)
        # default
        return False






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
    """Check we have a file a disk and return resolved."""
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exists.")
    if not path.is_file():
        raise NotAFileError(path)
    return path


def directory_exists(path: Path):
    """Check the provided path is an existing directory.
    
    Returns: resolved path.
    Raises: exception is not found or not a file.
    """
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exists.")
    if not path.is_dir():
        raise NotADirectoryError(path)
    return path    


class NotAFileError(Exception):
    """Raised if path is not a file."""
    def __init__(self, path):
        super().__init__(f"{path} is not a file.")

class NotADirectoryError(Exception):
    """Raised if path is not a file."""
    def __init__(self, path):
        super().__init__(f"{path} is not a directory.")

class IncompatibleTypeError(Exception):
    """Raised if types are incompatible."""
    def __init__(self, type1, type2):
        super().__init__(f"{type1} != {type2}")

class UnexpectedTypeError(Exception):
    """Raised if type is not supported."""
    def __init__(self, type):
        super().__init__(f"unexpected type : {type}")

class IncompatibleValueError(Exception):
    """Raised if value cannot be assigned to a type."""
    def __init__(self, io_id, type, value):
        super().__init__(f"Cannot assign {value} to {io_id} of type {type}") 


class CannotParseAdditionalInputParam(Exception):
    pass


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
    We also track if the parameter is optional or not
    (CWL encodes this information in the type declaration)
    """
    id: ParameterId
    # TODO make optional a parameter so it cannot be set
    # but only derived from type.
    # Check if we will still be able to retrieve it in the
    # type field validator.
    optional: bool = Field(False, exclude=True)
    type: Union[CWLArray, CWLTypes]

    # TODO TEST and FIX representation of cwl types.
    # This needs to be recursively parsing nested structures.
    @field_validator("type", mode="before")
    @classmethod
    def transform_type(cls, type: Any, optional: Any = None) -> Union[CWLTypes,CWLArray]:
        """Ingest any python type an transform it into a valid CWLType."""
        if isinstance(type, list):
            # CHECK for optional types
            if type[0] == 'null':
                # TODO feels a bit hacky to modify the model this way.
                # We could instead push that info in the type directly
                # if CWLType becomes a pydantic model.
                optional.data['optional'] = True
                return cls.transform_type(type[1])
            raise UnexpectedTypeError({type})
        if isinstance(type, dict):
            # TODO Test for arrays. Check if other representation are allowed.
            return CWLArray(**type)
        if isinstance(type, CWLTypes):
            return type
        else:
            try:
                return CWLTypes(type)
            except:
                raise UnexpectedTypeError({type})


    @field_serializer('type', when_used='always')
    def serialize_type(type: Union[CWLTypes,CWLArray]):
        """Define rules to serialize parameter types."""
        if isinstance(type, CWLTypes):
            serialized_type = type.value
        elif isinstance(type, CWLArray):
            # TODO maybe switch to standard form instead
            serialized_type = f"{type.items.value}[]"
            # TODO CHECK apparently this is not allowed.
            # serialized_type = {"items": type.items.value}
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
    value: Any = None
    optional: bool = Field(exclude= True)
    step_id: str

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

# def convert_to_string(value: Any, handler) -> str:
#     return handler(value.id)

"""WorkflowStepOutput are represented as string so we wrap the pydantic model to hide
from the callers.
"""
# WorkflowStepOutputId = Annotated[WorkflowStepOutput, WrapSerializer(convert_to_string)]

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

def filter_unused_optional(in_: Any, nxt: SerializerFunctionWrapHandler) -> list[WorkflowStepInput]:
    filtered_in_ = [input for input in in_ if input.source != "UNSET" ]
    return nxt(filtered_in_)

WorkflowStepInputs = Annotated[list[WorkflowStepInput], WrapSerializer(filter_unused_optional)]

WorkflowStepOutputs = Annotated[list[WorkflowStepOutput], []]


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
    in_: WorkflowStepInputs = Field(..., alias='in')
    out: WorkflowStepOutputs = Field(...)

    @property
    # TODO CHECK if we can type it to StepInputId
    def _inputs(self) -> dict[str, WorkflowStepInput]:
        """Generate a dict of WorkflowStepInputs for efficient retrieval."""
        return {input.id:input for input in self.in_}

    @property
    # TODO CHECK if we can type it to StepInputId
    def _outputs(self) -> dict[str, WorkflowStepInput]:
        """Generate a dict of WorkflowStepOutputs for efficient retrieval."""
        return {output.id:output for output in self.out}

    # TODO CHECK if we can type it to StepInputId
    scatter: Optional[list[str]] = Field(None) # ref to scatter inputs
    when: Optional[str] = Field(None) # ref to conditional execution clauses

    # TODO CHECK we may remove that later
    from_builder: Optional[bool] = Field(False, exclude=True)

    @field_serializer('out', when_used='always')
    def serialize_type(out:  WorkflowStepOutputs) -> list[str] :
        """When serializing, return only the list of ids."""
        return [output.id for output in out]

    @field_validator("out", mode="before")
    @classmethod
    def preprocess_workflow_step_output(cls, out) -> Any:
        """Wrap ids if we receive them as simple strings.
        
        This is required when loading a workflow with the cwl parser.
        """
        res = [{"id": wf_step_output} if isinstance(wf_step_output, str)
               else wf_step_output for wf_step_output in out]
        return res

    @field_validator("scatter", mode="before")
    @classmethod
    def preprocess_scatter(cls, out) -> Any:
        """Single string are allowed in CWL, so wrap them in an array."""
        if isinstance(out, str):
            out = [out]
        return out

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
    # TODO this method will eventually get removed
    def set_mutable_ios(self,
                        inputs: list[WorkflowStepInput],
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
        self._inputs = {input.id:input for input in inputs}
        self._outputs = {output.id:output for output in outputs}

        assignable_ins = []
        _inputs = {}
        for step_in in self.in_:
            process_input = inputs[step_in.id]
            # TODO change when we have a model. This is bug prone.
            in_type = process_input.type

            # TODO REMOVE we should create a parse Parameter model
            # rather than adhoc dictionaries.
            # optional can be missing when parsing additional input
            if "optional" in process_input:
                optional = process_input.optional
            else:
                optional = False
            
            if self.scatter:
                if step_in.id in self.scatter:
                    in_type = self.promote_cwl_type(in_type)

            values = step_in.model_dump()

            # TODO useless now, remove
            assignable_in = AssignableWorkflowStepInput(
                id=process_input.id,
                source=process_input.source,
                value=None,
                type=in_type,
                optional=optional,
                step_id=self.id
                )

            # assignable_in = AssignableWorkflowStepInput(
            #     **values,
            #     value=None,
            #     type=in_type,
            #     optional=optional,
            #     step_id=self.id
            #     )
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

    # TODO we probably could do better than having a adhoc serialization function
    def serialize_value(self, input):
        """Serialize input values."""
        # TODO check we cover all cases
        if input.type == CWLTypes.DIRECTORY:
            return {"class": "Directory", "location": Path(input.value).as_posix()}
        elif input.type == CWLTypes.FILE:
             return {"class": "File", "location": Path(input.value).as_posix()}
        else:
            return input.value


    def save_config(self, path = Path()) -> Path:
        """Save the workflow configuration.
        Args:
            - path : the path to the directory 
            in which to save the config.
        Returns: the path to the config file.
        """
        config = {input.id: self.serialize_value(input) for input in self.in_ if input.value is not None}
        
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
            # TODO CHECK how configurable this process is.
            # ex: we generate list but we could also generate some dictionaries.
            file.write(yaml.dump(config))
            return file_path 
    

class Process(BaseModel):
    """Process is the base class for Workflows,CommandLineTools
    (and also Expression Tools and Operations).

    see (https://www.commonwl.org/user_guide/introduction/basic-concepts.html)
    """
    model_config = ConfigDict(populate_by_name=True)
    
    id: ProcessId

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
            file.write(yaml.dump(serialized_process))
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
    inputs: list[CommandInputParameter]
    outputs: list[CommandOutputParameter]
    baseCommand: Optional[str] = None
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
        step_id = "step_"+ process.name
        run = process.id

        # TODO optional should be derived from type
        # TODO change. For now set source to "UNSET"
        inputs = [
            AssignableWorkflowStepInput(
                id= input.id,
                source= "UNSET",
                type= self._promote_cwl_type(input.type)
                    if scatter and input.id in scatter
                    else input.type,
                optional= input.optional,
                step_id= step_id
            )
            for input in process.inputs]

        outputs = [
            AssignableWorkflowStepOutput(
                id= output.id, 
                type= self._promote_cwl_type(output.type)
                    if scatter
                    else output.type,
                step_id= step_id
            )
            for output in process.outputs]
        
        # Generate additional inputs.
        # For example,if the conditional clause contains unknown inputs.
        # It could also be to generate fake inputs for wic compatibility.
        # TODO REVISIT that later after some use.

        # parse to workflow step input to detect basic problems early.
        # 
        if add_inputs:
            try:
                add_inputs = [WorkflowInputParameter(**input) for input in add_inputs]    
            except:
                raise CannotParseAdditionalInputParam("additional input description is invalid!")

        # input referenced in the when clause may or may not be already declared if the process.
        # If not, user must provide a description of it.
        # TODO we could evaluate the clause rather than having the user declare explicitly.
        if when:
            if not when_input_names:
                raise Exception("You need to specify which inputs are referenced in the when clause.")
            
            _add_inputs_ids = set([input.id for input in add_inputs]) if add_inputs else set()
            _process_inputs_ids = set([input.id for input in process.inputs])
            for when_input_name in when_input_names:
                if not (when_input_name in _process_inputs_ids):
                    if not(when_input_name in _add_inputs_ids):
                        raise Exception("Input in when clause unknown. Please add its declaration to add_inputs arguments.")
        
        if add_inputs:
            inputs = inputs + [
                AssignableWorkflowStepInput(
                    id= input.id,
                    source= "UNSET",
                    type= self._promote_cwl_type(input.type)
                        if scatter and input.id in scatter
                        else input.type,
                    optional= input.optional,
                    step_id= step_id
                )
            for input in add_inputs]
            
        self.step = WorkflowStep(
            scatter = scatter,
            when = when,
            id = step_id,
            run = run,
            in_ = inputs,
            out = outputs,
            from_builder = True,
            )

        # For a workflow, bubble up values assigned to its steps.
        # The become values of the workflow inputs.
        if isinstance(process, Workflow):
            for step in process.steps:
                for input in step.in_:
                    # TODO maybe create a workflow subclass for assignable workflow instead?
                    if isinstance(input, AssignableWorkflowStepInput):
                        if input.source in self.step._inputs:
                            self.step._inputs[input.source].value = input.value
                            assignable_step_input = self.step._inputs[input.source]
                            print(assignable_step_input)


    # TODO this could be move to the CWLModel pydantic model once we have it.
    def _promote_cwl_type(self, type: CWLTypes):
        """When scattering over some inputs, we will provide arrays of value of the
        original types.
        """
        if isinstance(type, CWLArray):
            #TODO FIX
            raise NotImplementedError("scattering CWLArray is not yet implemented.")
        return CWLArray(items=type)


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

        # TODO Many possible strategies here: 
        # We could change that, make that a user provided option,
        # generate simpler names if no clash are detected 
        # or provide ability for aliases...
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
                # Only create workflows inputs and connect to them them
                # if step inputs are not already connected to another step output.
                # TODO switch to continue logic
                if input.source == 'UNSET':

                    # Ignore unset optional inputs
                    # TODO CHECK again but nothing else seems to be possible.
                    # IMO this is a problem with the standard.
                    if input.optional and input.value is None:
                        continue

                    # if a step input is also a step output,
                    # and this step output is link to other step inputs,
                    # then we can generate a default value for this input
                    # and bubble it up to the workflow input value
                    # this also allow further manual customization.
                    # TODO we could also expose that the user and have him customized
                    # the generated name.
                    # TODO CHECK this logic again, it may probably be written more simply.
                    if input.id in step._outputs:
                        _step_id = step.id
                        _same_name_output = step._outputs[input.id]
                        _ref = _step_id + "/" + _same_name_output.id
                        for _other_step in kwds.get("steps"):
                            for _input in _other_step.in_:
                                if _input.source == _ref:
                                    if _input.type != CWLTypes.DIRECTORY:
                                        # CHECK probably untrue, what about files, array of files etc...
                                        raise Exception("should only be directory here!")
                                    else:
                                        # TODO the last thing to do is to create a input value 
                                        # that we can pass to the source workflow input.
                                        # NOTE there is a bug in cwl that prevents to create nested directories.
                                        # it seems that when copying back staged data, cwl only copies the last
                                        # directory. Name clashes will occur if several inputs have the same name.
                                        # input.value = Path() / _step_id / input.id
                                        input.value = Path() / (_step_id + "__" + input.id)
                                        # TODO REMOVE temp hack for conveniently running those workflows,
                                        # figure out how to tell cwl to create the directories first
                                        # something about listing files or something
                                        input.value.mkdir(parents=True, exist_ok=True)

                    
                    # TODO create method, we could also wrap CWLTypes in a pydantic model
                    input_type = input.type
                    # TODO Remove once we fix type system.
                    input_type = input_type.model_dump() if isinstance(input_type, CWLArray) else input_type.value
                    workflow_input_id = generate_workflow_io_id(id, step.id, input.id)
                    workflow_input = WorkflowInputParameter(
                        id= workflow_input_id,
                        type= input_type
                        )
                    input.source = workflow_input_id
                    workflow_inputs.append(workflow_input)

            for output in step.out:
                    output_type = output.type
                    # TODO CHANGE that once we have review the type system.
                    output_type = output_type.model_dump() if isinstance(output_type, CWLArray) else output_type.value
                    workflow_output_id = generate_workflow_io_id(id, step.id, output.id)

                    workflow_output = WorkflowOutputParameter(
                        id = workflow_output_id,
                        type= output_type,
                        outputSource= step.id + "/" + output.id
                    )
                    workflow_outputs.append(workflow_output)

            # TODO That is where a context of loaded CLTs could be helpful.
            # So we don't keep reloading the same models.
            # Detect if we need to add subworkflowFeatureRequirement.
            # TODO we could remove most of the code here.
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

