cwlVersion: v1.2
class: Workflow

inputs:
  # workflow input, can be named anything
  message: string

outputs:
  # workflow output, here the result of uppercase
  uppercase_message: 
    type: string
    outputSource: uppercase/uppercase_message

steps:  
  uppercase:
    run: uppercase.cwl
    in:
      message: message
    out: [uppercase_message]