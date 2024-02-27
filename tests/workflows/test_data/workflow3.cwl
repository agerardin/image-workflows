cwlVersion: v1.2
class: Workflow

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
    run: uppercase2_wic_compatible3.cwl
    in:
      message: echo/message_string
    out: [uppercase_message]