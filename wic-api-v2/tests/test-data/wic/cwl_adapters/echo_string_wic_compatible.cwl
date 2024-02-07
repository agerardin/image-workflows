cwlVersion: v1.2

class: CommandLineTool

baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1

  stdout_string:  # exactly the same name as the actual output named stdout
    type: string
  # Doesn't even have an inputBinding: so it is unused, fake news!

outputs:
  stdout_string:
    type: string
    outputBinding:
      glob: stdout
      loadContents: True
      outputEval: $(self[0].contents)

stdout: stdout