cwlVersion: v1.2
class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}

baseCommand: echo

stdout: stdout_uppercase

inputs:
  message:
    type: string
    inputBinding:
      position: 1

  uppercase_message: 
    type: string
      
outputs:
  uppercase_message: 
    type: string
    outputBinding:
      glob: stdout_uppercase
      loadContents: True
      outputEval: |
        $(self[0].contents.toUpperCase())