cwlVersion: v1.2
class: CommandLineTool

baseCommand: echo
inputs:
  message:
    type: string
    inputBinding:
      position: 1
stdout: output.txt
outputs: 
  out_message:
    type: stdout
