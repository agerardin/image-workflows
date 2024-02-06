cwlVersion: v1.2
class: Workflow

doc: |-
  It seems branching is only possible at the workflow level.
  (we cannot have a workflow with branching steps).
  See how can add extra inputs to steps so we can tests for them,
  eventhough the underlying clt does not declare those.
  Since we need to define how to deal with the conditional,
  we had the pickValue to disambiguate processing.
  Note that if no conditions are met, this will fail.

requirements:
  InlineJavascriptRequirement: {}
  MultipleInputFeatureRequirement: {}

inputs:
  msg: string
  should_uppercase: int

outputs:
  transformed_string:
    type: string
    outputSource: 
      - uppercase/uppercase_message
      - lowercase/lowercase_message
    pickValue: first_non_null
steps:
  echo:
    run: echo_string.cwl
    in:
      message: msg
    out: [message_string]

  uppercase:
    run: uppercase.cwl
    when: $(inputs.should_execute < 2)
    in:
      should_execute: should_uppercase
      message: echo/message_string
    out: [uppercase_message]

  lowercase:
    run: lowercase.cwl
    when: $(inputs.should_execute > 5)
    in:
      should_execute: should_uppercase
      message: echo/message_string
    out: [lowercase_message]