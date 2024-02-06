cwlVersion: v1.2
class: Workflow

inputs:
  msg: string

outputs:
  uppercase_message: 
    type: string
    outputSource: workflow1/message_string

steps:
  workflow1:
    run: gotcha_workflow1.cwl
    in:
      message: msg
    out: [message_string]