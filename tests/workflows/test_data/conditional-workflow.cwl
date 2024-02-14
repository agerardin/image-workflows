cwlVersion: v1.2
class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  msg: string[]
  should_touch: int

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
  touch:
    scatter: [touchfiles]
    run: touch_single.cwl
    when: $(inputs.should_execute < 1)
    in:
      should_execute: should_touch 
      touchfiles: echo-uppercase-wf/uppercase_message
    out: [output]