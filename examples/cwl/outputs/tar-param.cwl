#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
baseCommand: [tar, --extract]
inputs:
  # tar file and extract file as expected
  tarfile:
    type: File
    inputBinding:
      prefix: --file
  extractfile:
    type: string
    inputBinding:
      position: 1
outputs:
  # the output (extracted_file)
  # see how the actual filename is derived from the input filename
  # Is it because all files are staged, so they can be rename arbitrarily afterwards?
  extracted_file:
    type: File
    outputBinding:
      glob: $(inputs.extractfile)