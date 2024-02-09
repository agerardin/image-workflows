Workflow(
    id='file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/wf3',
    inputs=[WorkflowInputParameter(id='wf3/step_echo_string/message', type='string')],
    outputs=[
        WorkflowOutputParameter(
            id='wf3/step_echo_string/message_string',
            type='string',
            outputSource='step_echo_string/message_string'
        ),
        WorkflowOutputParameter(
            id='wf3/step_uppercase2_wic_compatible2/uppercase_message',
            type='string',
            outputSource='step_uppercase2_wic_compatible2/uppercase_message'
        )
    ],
    steps=[
        WorkflowStep(
            id='step_echo_string',
            run='file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/echo_string.cwl
',
            in_=[WorkflowStepInput(id='message', source='UNSET', type='string')],
            out=['message_string'],
            from_builder=True
        ),
        WorkflowStep(
            id='step_uppercase2_wic_compatible2',
            run='file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/wic/cwl_adapters/up
percase2_wic_compatible2.cwl',
            in_=[
                WorkflowStepInput(id='message', source='step_echo_string/message_string', type='string'),
                WorkflowStepInput(id='uppercase_message', source='step_echo_string/message_string', type='string')
            ],
            out=['uppercase_message'],
            from_builder=True
        )
    ],
    requirements=None,
    from_builder=True,
    class_='Workflow',
    cwlVersion='v1.2'
)