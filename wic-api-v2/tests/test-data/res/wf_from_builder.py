Workflow(
    id='wf3',
    inputs=[WorkflowInputParameter(id='wf3/step_echo_string/message', type='TYPE_MISSING')],
    outputs=[
        WorkflowOutputParameter(
            id='wf3/step_echo_string/message_string',
            type='TYPE_MISSING',
            outputSource='step_echo_string/message_string'
        ),
        WorkflowOutputParameter(
            id='wf3/step_uppercase2_wic_compatible2/uppercase_message',
            type='TYPE_MISSING',
            outputSource='step_uppercase2_wic_compatible2/uppercase_message'
        )
    ],
    steps=[
        WorkflowStep(
            id='step_echo_string',
            run='file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/cwl/echo_s
tring.cwl',
            in_=[WorkflowStepInput(id='message', source='UNSET')],
            out=['message_string'],
            from_builder=True
        ),
        WorkflowStep(
            id='step_uppercase2_wic_compatible2',
            run='file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/tests/test-data/wic/cwl_ad
apters/uppercase2_wic_compatible2.cwl',
            in_=[
                WorkflowStepInput(id='message', source='step_echo_string/message_string'),
                WorkflowStepInput(id='uppercase_message', source='step_echo_string/message_string')
            ],
            out=['uppercase_message'],
            from_builder=True
        )
    ],
    requirements=None,
    from_builder=True,
    class_='Workflow'
)