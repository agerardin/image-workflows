cwlVersion: v1.2
class: Workflow


inputs:
  msg: string

outputs:
  msg_file: 
    type: File
    outputSource: echo/out_message

steps:
  echo:
    run: echo_output_file.cwl
    in:
      message: msg
    out: [out_message]