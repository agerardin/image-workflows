from api import (
    Step,
    StepIO,
    IO,
    CLT,
    Workflow
)



inputA = IO[int]("inputA")
outputB = IO[str]("outputB")
clt1 = CLT([inputA],[outputB])
step1 = Step(clt1)

# input assignment abstracted away in __set_attr__
# we need also to enforce type checking
# not sure how optional works here
step1.inputs[0].value = 2
step1.inputs[0].value = "str"


inputB = IO[str]("inputB")
outputC = IO[str]("outputC")
clt2 = CLT([inputB],[outputC])
step2 = Step(clt2)

# setting to source will be abstracted away in __set_attr__
# step2.inputB = step1.outputB
step2.inputs[0].source = step1.outputs[0]
# this will also set step1.outputs[0].sink = step2.inputs[0]

# Worflow(["inputA"],["outputC"],[step1, step2])
wf1 = Workflow([step1.inputs[0]],[step2.outputs[0]],[step1,step2])

assert wf1.steps[1].inputs[0].source == step1.outputs[0]

# we can wrap a workflow as a step
# now we can only connect its visible IOs to other steps
step3 = Step(wf1)
# print(wf1.inputs)

inputC = IO[int]("inputC")
outputD = IO[int]("outputD")
clt3 = CLT([inputC],[outputD])
step4 = Step(clt3)

# This is a cycle and this should fail
# This may be hard to detect. Let the cwl compiler deal with it?
step4.outputs[0].source = step4.inputs[0]

step4.inputs[0].source = step3.outputs[0]

# if we scatter, we need to promote typing of inputs.
# outputs are also promoted
wf2 = Workflow(wf1.inputs,[outputD],[step3,step4],scatter=["fdfds"])


wf2.compile()
