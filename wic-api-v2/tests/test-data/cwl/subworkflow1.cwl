cwlVersion: v1.2
class: Workflow

inputs:
  # workflow input, can be named anything
  msg: string

outputs:
  # workflow output, here the result of uppercase
  uppercase_message: 
    type: string
    outputSource: uppercase/uppercase_message

steps:  
  uppercase:
    run: uppercase.cwl
    in:
      message: msg
    out: [uppercase_message]