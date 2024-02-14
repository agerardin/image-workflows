class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/tests/conditional-workflow.cwl
inputs:
- id: msg
  type: string[]
- id: should_touch
  type: int
outputs:
- id: new_file
  outputSource: touch/output
  type: File[]
requirements:
- class: InlineJavascriptRequirement
- class: ScatterFeatureRequirement
- class: SubworkflowFeatureRequirement
steps:
- id: echo-uppercase-wf
  in:
  - id: msg
    source: msg
  out:
  - uppercase_message
  run: workflow3.cwl
  scatter:
  - msg
- id: touch
  in:
  - id: should_execute
    source: should_touch
  - id: touchfiles
    source: echo-uppercase-wf/uppercase_message
  out:
  - output
  run: touch_single.cwl
  scatter:
  - touchfiles
  when: $(inputs.should_execute < 1)
