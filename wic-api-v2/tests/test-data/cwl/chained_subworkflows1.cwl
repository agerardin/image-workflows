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
    run: workflow3.cwl
    scatter: [msg]
    in:
      msg: msg
    out: [uppercase_message]
  echo-uppercase-wf2:
    run: workflow3.cwl
    scatter: [msg]
    in:
      msg: echo-uppercase-wf/uppercase_message
    out: [uppercase_message]    
  touch:
    scatter: [touchfiles]
    run: touch_single.cwl
    in: 
      touchfiles: echo-uppercase-wf/uppercase_message
    out: [output]