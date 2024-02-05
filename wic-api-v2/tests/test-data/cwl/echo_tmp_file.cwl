cwlVersion: v1.2
class: CommandLineTool

baseCommand: echo
inputs:
  message:
    type: string
    inputBinding:
      position: 1
outputs: 
  # capture stdout and write it to a file, but with a random temp name
  out_message:
    type: stdout
