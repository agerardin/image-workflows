cwlVersion: v1.0

class: CommandLineTool

baseCommand: touch

inputs:
  input_string:
    type: string
    inputBinding:
      position: 1

outputs:
  stdout:
    type: File
    outputBinding:
      glob: stdout

stdout: stdout