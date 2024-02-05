#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [tar, --extract]
inputs:
  tarfile:
    type: File
    inputBinding:
      prefix: --file
outputs:
  # CHECK output is named example_out!
  example_out:
    type: File
    outputBinding:
      glob: hello.txt
