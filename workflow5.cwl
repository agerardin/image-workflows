class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/tests/workflows/test_data/workflow5.cwl
inputs:
- id: msg
  type: string
outputs:
- id: file
  outputSource: touch/output
  type: File
steps:
- id: echo
  in:
  - id: message
    source: msg
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/tests/workflows/test_data/echo_string.cwl
- id: touch
  in:
  - id: touchfiles
    source: echo/message_string
  out:
  - output
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/tests/workflows/test_data/touch_single.cwl
