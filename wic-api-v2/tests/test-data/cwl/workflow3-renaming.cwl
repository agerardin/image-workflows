cwlVersion: v1.2
class: Workflow

doc: |-
  Here we renamed the inputs and demonstrate it still works

inputs:
  msg: string

outputs:
  uppercase_message: 
    type: string
    outputSource: uppercase/uppercase_message

steps:
  echo:
    run: echo_string.cwl
    in:
      message: msg
    out: [message_string]

  uppercase:
    run: uppercase.cwl
    in:
      message: echo/message_string
    out: [uppercase_message]