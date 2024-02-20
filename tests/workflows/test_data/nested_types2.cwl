#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool

label: generate a cwl string

doc: Take a user input and generate a cwl string for it.

baseCommand: echo

inputs:
  message:
    type:
      type: array
      items:
        type: array
        items:
          type: array
          items:
            string
    inputBinding:
      position: 1

stdout: message

outputs:
  message_string:
    type:
      type: array
      items:
        type: array
        items:
          type: array
          items:
            string
    outputBinding:
      glob: message
      loadContents: True
      outputEval: $(self[0].contents)