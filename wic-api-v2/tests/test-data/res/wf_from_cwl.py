Workflow(
    id='file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/workflow7.cwl',
    inputs=[WorkflowInputParameter(id='msg', type='string')],
    outputs=[
        WorkflowOutputParameter(id='uppercase_message', type='string', outputSource='uppercase/uppercase_message')
    ],
    steps=[
        WorkflowStep(
            id='echo',
            run='echo_string.cwl',
            in_=[WorkflowStepInput(id='message', source='msg')],
            out=['message_string'],
            from_builder=False
        ),
        WorkflowStep(
            id='uppercase',
            run='uppercase2_wic_compatible2.cwl',
            in_=[
                WorkflowStepInput(id='message', source='echo/message_string'),
                WorkflowStepInput(id='uppercase_message', source='echo/message_string')
            ],
            out=['uppercase_message'],
            from_builder=False
        )
    ],
    requirements=None,
    from_builder=False,
    class_='Workflow'
)