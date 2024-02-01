#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: Workflow

requirements:
  ScatterFeatureRequirement: {}

inputs:
  message_array:
    type: string[]
    inputBinding:
      prefix: -M=
      itemSeparator: ","
      separate: false
      position: 1

steps:
  echo:
    run: echo.cwl
    scatter: message
    in:
      message: message_array
    out: []

outputs: []

