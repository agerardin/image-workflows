cwlVersion: v1.2
class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}

inputs:
  message: string
outputs:
  lowercase_message: string

expression: |
  ${ return {"lowercase_message": inputs.message.toLowerCase()}; }