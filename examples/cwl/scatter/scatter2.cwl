#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: Workflow

requirements:
  ScatterFeatureRequirement: {}

inputs:
  message_array:
    type:
      type: array
      items: string

steps:
  echo:
    run: echo.cwl
    scatter: message
    in:
      message: message_array
    out: []

outputs: []

