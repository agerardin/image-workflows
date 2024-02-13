cwlVersion: v1.2
class: Workflow

requirements:
  ScatterFeatureRequirement: {}

inputs:
  msg: string[]

outputs:
  new_file:
    type: File[]
    outputSource: touch/output

steps:
  echo:
    scatter: [message]
    run: echo_string.cwl
    in:
      message: msg
    out: [message_string]

  touch:
    scatter: [touchfiles]
    run: touch_single.cwl
    in:
      touchfiles: echo/message_string
    out: [output]