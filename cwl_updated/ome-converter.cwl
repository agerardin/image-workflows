#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0

label: OME Zarr Converter

doc: |-
  This WIPP plugin converts BioFormats supported data types to the OME Zarr file format.
  https://github.com/PolusAI/polus-plugins/tree/master/formats/ome-converter-plugin

# See https://github.com/PolusAI/workflow-inference-compiler/blob/master/docker_remove_entrypoints.py
baseCommand: python3
arguments: ["-m", "polus.plugins.formats.ome_converter"]

requirements:
  DockerRequirement:
    dockerPull: jakefennick/ome-converter-plugin:0.3.2
  # See https://www.commonwl.org/v1.0/CommandLineTool.html#InitialWorkDirRequirement
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.outDir)
      writable: true  # Output directories must be writable
  InlineJavascriptRequirement: {}
# NOTE: polusai/ome-converter-plugin:0.3.1 uses the base image
# polusai/bfio:2.3.2 which now un-bundles the java maven package
# ome:formats-gpl:7.1.0 due to licensing reasons.
# To avoid requiring network access at runtime, in the bfio Dockerfile
# it is pre-installed and saved in ~/.m2/  However, by default
# CWL hides all environment variables (including HOME), so we need to
# set HOME here so that at runtime we get a cache hit on the maven install.
  EnvVarRequirement:
# See https://www.commonwl.org/user_guide/topics/environment-variables.html
    envDef:
      HOME: /home/polusai

inputs:
  inpDir:
    label: Input generic data collection to be processed by this plugin
    doc: |-
      Input generic data collection to be processed by this plugin
    type: Directory
    inputBinding:
      prefix: --inpDir

  filePattern:
    label: A filepattern, used to select data for conversion
    doc: |-
      A filepattern, used to select data for conversion
    type: string
    inputBinding:
      prefix: --filePattern

  fileExtension:
    label: The file extension
    doc: |-
      The file extension
    type: string
    inputBinding:
      prefix: --fileExtension
    default: "default"  # enum: .ome.tiff, .ome.zarr, default

  outDir:
    label: Output collection
    doc: |-
      Output collection
    type: Directory
    inputBinding:
      prefix: --outDir

outputs:
  outDir:
    label: Output collection
    doc: |-
      Output collection
    type: Directory
    outputBinding:
      glob: $(inputs.outDir.basename)

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl

# manifest: https://raw.githubusercontent.com/PolusAI/polus-plugins/master/formats/ome-converter-plugin/plugin.json