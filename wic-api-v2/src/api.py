from model import (
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
step1.inputs[0].value = 2

inputB = IO[str]("inputB")
outputC = IO[str]("outputC")
clt2 = CLT([inputB],[outputC])
step2 = Step(clt2)

# setting to source will be abstracted away in __set_attr__
step2.inputs[0].source = step1.outputs[0]
# this will also set step1.outputs[0].sink = step2.inputs[0]

wf1 = Workflow([step1.inputs[0]],[step2.outputs[0]],[step1,step2])

assert wf1.steps[1].inputs[0].source == step1.outputs[0]

# we can wrap a workflow as a step
# now we can only connect its visible IOs to other steps
step3 = Step(wf1)
print(wf1.inputs)

inputC = IO[int]("inputC")
clt3 = CLT([inputC],[])
step4 = Step(clt3)

step4.inputs[0].source = step3.outputs[0]

# if we scatter, we need to promote typing of inputs.
# outputs are also promoted
wf2 = Workflow(wf1.inputs,[],[step3,step4],scatter=True)

wf2.compile()
