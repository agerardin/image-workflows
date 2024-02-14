class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/conditional_workflow_generated.cwl
inputs:
- id: conditional_workflow_generated___step_workflow3___msg
  type: string
- id: conditional_workflow_generated___step_touch_single___should_execute
  type: int
outputs:
- id: conditional_workflow_generated___step_workflow3___uppercase_message
  outputSource: step_workflow3/uppercase_message
  type: string
- id: conditional_workflow_generated___step_touch_single___output
  outputSource: step_touch_single/output
  type: File
requirements:
- class: SubworkflowFeatureRequirement
- class: InlineJavascriptRequirement
steps:
- id: step_workflow3
  in:
  - id: msg
    source: conditional_workflow_generated___step_workflow3___msg
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/tests/workflow3.cwl
- id: step_touch_single
  in:
  - id: touchfiles
    source: step_workflow3/uppercase_message
  - id: should_execute
    source: conditional_workflow_generated___step_touch_single___should_execute
  out:
  - output
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wic-api-v2/src/tests/touch_single.cwl
  when: $(inputs.should_execute < 1)
