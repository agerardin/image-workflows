cwlVersion: v1.2
class: Workflow

inputs:
  # ids can be anything
  msg: string
  # this is a optional param
  unused_msg: string?
  # we can have default value as well
  defaulted_msg: 
    type: string 
    default: "_suffix"

outputs:
  # output can also be anything
  msg_file: 
    type: File
    # must be link to a step output
    outputSource: echo/out_message
  uppercase_message: 
    type: string
    outputSource: uppercase/uppercase_message

steps:
  echo:
    run: echo_output_file.cwl
    in:
      # we can link to a workflow input
      message: msg
    
    # we need to declare the output of the tool we will use later.
    # if other outputs exists, they are ignored
    out: [out_message]

  uppercase:
    run: uppercase_from_file.cwl
    in:
      # reference dependence on previous step
      message: echo/out_message
    out: [uppercase_message]