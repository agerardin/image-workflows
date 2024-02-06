cwlVersion: v1.2
class: Workflow

doc: |-
  Check here how are the input prefixed with my/ !

inputs:
  my/msg: string

outputs:
  uppercase_message: 
    type: string
    outputSource: uppercase/uppercase_message

steps:
  echo:
    run: echo_string.cwl
    in:
      message: my/msg
    out: [message_string]

  uppercase:
    run: uppercase.cwl
    in:
      message: echo/message_string
    out: [uppercase_message]