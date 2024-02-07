#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
baseCommand: touch
inputs:
  filename:
    type: string
    inputBinding:
      position: 1
outputs:
  output:
    type: File
    outputBinding:
      glob: "*"