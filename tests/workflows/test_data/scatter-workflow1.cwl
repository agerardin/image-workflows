cwlVersion: v1.2
class: Workflow

inputs:
  # here we wanted to pass a array so we need 
  # to do a bunch of modification
  msg: string[]
  # this is a optional param
  # unused_msg: string?
  # we can have default value as well
  defaulted_msg: 
    type: string 
    default: "_suffix"

outputs:
  # first all ouputs have to be promoted to arrays
  # uppercase_message: 
  #   type: string[]
  #   outputSource: uppercase/uppercase_message
  new_files: 
    type: File[]
    # must be link to a step output
    outputSource: touch/output

# We need to add this requirement
requirements:
  ScatterFeatureRequirement: {}

steps:
  echo:
    run: echo_output_file.cwl
    scatter: message
    in:
      message: msg
    out: [out_message]

  uppercase:
    run: uppercase_from_file.cwl
    scatter: message
    in:
      # reference dependence on previous step
      message: echo/out_message
    out: [uppercase_message]

  touch: 
    run: touch.cwl
    in: 
      touchfiles: uppercase/uppercase_message
    out: [output]