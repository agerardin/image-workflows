cwlVersion: v1.2
class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}

inputs:
  msg: string

outputs:
  new_file:
    type: File
    outputSource: touch/output

steps:
  echo-uppercase-wf:
    run: workflow2.cwl
    in:
      msg: msg
    out: [uppercase_message]
  touch:
    run: touch_single.cwl
    in: 
      touchfiles: echo-uppercase-wf/uppercase_message
    out: [output]