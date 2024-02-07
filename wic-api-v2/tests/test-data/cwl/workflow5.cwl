cwlVersion: v1.2
class: Workflow

doc: |-
  Can this be translated with wic using explicit edges?

inputs:
  msg: string

outputs:
  file: 
    type: File
    outputSource: touch/output

steps:
  echo:
    run: echo_string.cwl
    in:
      message: msg
    out: [message_string]

  touch:
    run: touch_single.cwl
    in:
      touchfiles: echo/message_string
    out: [output]