cwlVersion: v1.2
class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}

inputs:
  message:
    type: File
    inputBinding:
      loadContents: True
  
outputs:
  uppercase_message: string

expression: |
  ${ return {"uppercase_message": inputs.message.contents.toUpperCase()}; }