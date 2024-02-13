class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/tests/scatter-workflow1.cwl
inputs:
- id: defaulted_msg
  type: string
- id: msg
  type: string[]
outputs:
- id: new_files
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
  - out_message
  run: echo_output_file.cwl
- id: touch
  in:
  - id: touchfiles
    source: uppercase/uppercase_message
  out:
  - output
  run: touch.cwl
- id: uppercase
  in:
  - id: message
    source: echo/out_message
  out:
  - uppercase_message
  run: uppercase_from_file.cwl
