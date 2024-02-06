cwlVersion: v1.2
class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}

inputs:
  msg: string[]

outputs:
  new_file:
    type: File[]
    outputSource: touch/output

steps:
  echo-uppercase-wf:
    scatter: [msg]
    run: workflow2.cwl
    in:
      msg: msg
    out: [uppercase_message]
  touch:
    run: touch.cwl
    in: 
      touchfiles: echo-uppercase-wf/uppercase_message
    out: [output]