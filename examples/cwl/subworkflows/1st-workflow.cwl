#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: Workflow

# input tarball is a File (a record with a class attribute set to "File")
inputs:
  tarball: File
  name_of_file_to_extract: string

# output will be file coming from the compile steps.
outputs:
  compiled_class:
    type: File
    outputSource: compile/classfile

steps:
  untar:
    run: ../outputs/tar-param.cwl
    in:
      # pass in the file from the inputs
      tarfile: tarball
      # and also the name of the file inside the archive to extract
      extractfile: name_of_file_to_extract
    out: [extracted_file]

  compile:
    run: ../inputs/arguments.cwl
    in:
      src: untar/extracted_file
    out: [classfile]