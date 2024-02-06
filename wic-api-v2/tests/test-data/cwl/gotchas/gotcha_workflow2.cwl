cwlVersion: v1.2
class: Workflow

inputs:
  msg: string

outputs:
  uppercase_message: 
    type: string
    outputSource: workflow2/message_string

steps:
  workflow2:
    run: gotcha_workflow2.cwl
    in:
      message: msg
    out: [message_string]