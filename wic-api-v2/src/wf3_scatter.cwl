class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/wf3_scatter.cwl
inputs:
- id: wf3_scatter___step_echo_string___message
  type: string[]
outputs:
- id: wf3_scatter___step_echo_string___message_string
  outputSource: step_echo_string/message_string
  type: string[]
- id: wf3_scatter___step_uppercase2_wic_compatible3___uppercase_message
  outputSource: step_uppercase2_wic_compatible3/uppercase_message
  type: string[]
requirements:
- class: ScatterFeatureRequirement
steps:
- id: step_echo_string
  in:
  - id: message
    source: wf3_scatter___step_echo_string___message
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/tests/echo_string.cwl
  scatter:
  - message
- id: step_uppercase2_wic_compatible3
  in:
  - id: message
    source: step_echo_string/message_string
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/tests/uppercase2_wic_compatible3.cwl
  scatter:
  - message
