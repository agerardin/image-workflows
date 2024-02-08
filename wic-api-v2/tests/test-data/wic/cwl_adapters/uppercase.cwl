cwlVersion: v1.0  # We only need v1.0 in this file
class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}

# NOTE: This is essentially an ExpressionTool
baseCommand: 'true'  # Use quotes to prevent yaml syntax from turning true into a boolean

stdout: stdout_uppercase

inputs:
  message:
    type: string
    default: hello
    inputBinding:
      position: 1

  uppercase_message:
    type: string?  # Use ? because these fake-news inputs should all be optional
      
outputs:
  uppercase_message:
    type: string
    outputBinding:
      outputEval: $(inputs.message.toUpperCase())