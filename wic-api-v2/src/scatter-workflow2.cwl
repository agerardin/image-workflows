class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/tests/scatter-workflow2.cwl
inputs:
- id: msg
  type: string[]
outputs:
- id: new_file
  outputSource: touch/output
  type: File[]
requirements:
- class: ScatterFeatureRequirement
steps:
- id: echo
  in:
  - id: message
    source: msg
  out:
  - message_string
  run: echo_string.cwl
  scatter:
  - message
- id: touch
  in:
  - id: touchfiles
    source: echo/message_string
  out:
  - output
  run: touch_single.cwl
  scatter:
  - touchfiles
