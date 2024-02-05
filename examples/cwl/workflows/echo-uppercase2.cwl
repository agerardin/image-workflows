cwlVersion: v1.2
class: Workflow

requirements:
  InlineJavascriptRequirement: {}

inputs:
  message: string

outputs:
  out:
    type: string
    outputSource: uppercase/uppercase_message

steps:
  echo:
    run: ../basic/echo.cwl
    in:
      message: message
    out: [out]
  uppercase:
    run: ../basic/uppercase2.cwl
    in:
      message:
        source: echo/out
    out: [uppercase_message]