cwlVersion: v1.2
class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}

inputs:
  message: string
outputs:
  uppercase_message: string
  uppercase_message2: string

expression: |
  ${ return [
    {"uppercase_message": inputs.message.toUpperCase()},
    {"uppercase_message2": inputs.message.toUpperCase()}
              ]; }