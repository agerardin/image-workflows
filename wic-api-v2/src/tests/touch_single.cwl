#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
baseCommand: touch
inputs:
  touchfiles:
    type: string
    inputBinding:
      position: 1
outputs:
  output:
    type: File
    outputBinding:
      glob: "*"