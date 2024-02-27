class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/wf_image_processing.cwl
inputs:
- id: wf_image_processing___step_BbbcDownload___name
  type: string
- id: wf_image_processing___step_BbbcDownload___outDir
  type: Directory
- id: wf_image_processing___step_FileRenaming___filePattern
  type: string
- id: wf_image_processing___step_FileRenaming___mapDirectory
  type: string
- id: wf_image_processing___step_FileRenaming___outDir
  type: Directory
- id: wf_image_processing___step_FileRenaming___outFilePattern
  type: string
- id: wf_image_processing___step_OmeConverter___fileExtension
  type: string
- id: wf_image_processing___step_OmeConverter___filePattern
  type: string
- id: wf_image_processing___step_OmeConverter___outDir
  type: Directory
- id: wf_image_processing___step_Montage___filePattern
  type: string
- id: wf_image_processing___step_Montage___layout
  type: string
- id: wf_image_processing___step_Montage___outDir
  type: Directory
- id: wf_image_processing___step_ImageAssembler___outDir
  type: Directory
- id: wf_image_processing___step_PrecomputeSlide___filePattern
  type: string
- id: wf_image_processing___step_PrecomputeSlide___imageType
  type: string
- id: wf_image_processing___step_PrecomputeSlide___outDir
  type: Directory
- id: wf_image_processing___step_PrecomputeSlide___pyramidType
  type: string
outputs:
- id: wf_image_processing___step_BbbcDownload___outDir
  outputSource: step_BbbcDownload/outDir
  type: Directory
- id: wf_image_processing___step_FileRenaming___outDir
  outputSource: step_FileRenaming/outDir
  type: Directory
- id: wf_image_processing___step_OmeConverter___outDir
  outputSource: step_OmeConverter/outDir
  type: Directory
- id: wf_image_processing___step_Montage___outDir
  outputSource: step_Montage/outDir
  type: Directory
- id: wf_image_processing___step_ImageAssembler___outDir
  outputSource: step_ImageAssembler/outDir
  type: Directory
- id: wf_image_processing___step_PrecomputeSlide___outDir
  outputSource: step_PrecomputeSlide/outDir
  type: Directory
steps:
- id: step_BbbcDownload
  in:
  - id: name
    source: wf_image_processing___step_BbbcDownload___name
  - id: outDir
    source: wf_image_processing___step_BbbcDownload___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/cwl/BbbcDownload.cwl
- id: step_FileRenaming
  in:
  - id: filePattern
    source: wf_image_processing___step_FileRenaming___filePattern
  - id: inpDir
    source: step_BbbcDownload/outDir
  - id: mapDirectory
    source: wf_image_processing___step_FileRenaming___mapDirectory
  - id: outDir
    source: wf_image_processing___step_FileRenaming___outDir
  - id: outFilePattern
    source: wf_image_processing___step_FileRenaming___outFilePattern
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/cwl/FileRenaming.cwl
- id: step_OmeConverter
  in:
  - id: fileExtension
    source: wf_image_processing___step_OmeConverter___fileExtension
  - id: filePattern
    source: wf_image_processing___step_OmeConverter___filePattern
  - id: inpDir
    source: step_FileRenaming/outDir
  - id: outDir
    source: wf_image_processing___step_OmeConverter___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/cwl/OmeConverter.cwl
- id: step_Montage
  in:
  - id: filePattern
    source: wf_image_processing___step_Montage___filePattern
  - id: inpDir
    source: step_OmeConverter/outDir
  - id: layout
    source: wf_image_processing___step_Montage___layout
  - id: outDir
    source: wf_image_processing___step_Montage___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/cwl/Montage.cwl
- id: step_ImageAssembler
  in:
  - id: imgPath
    source: step_OmeConverter/outDir
  - id: outDir
    source: wf_image_processing___step_ImageAssembler___outDir
  - id: stitchPath
    source: step_Montage/outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/cwl/ImageAssembler.cwl
- id: step_PrecomputeSlide
  in:
  - id: filePattern
    source: wf_image_processing___step_PrecomputeSlide___filePattern
  - id: imageType
    source: wf_image_processing___step_PrecomputeSlide___imageType
  - id: inpDir
    source: step_ImageAssembler/outDir
  - id: outDir
    source: wf_image_processing___step_PrecomputeSlide___outDir
  - id: pyramidType
    source: wf_image_processing___step_PrecomputeSlide___pyramidType
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-pipelines/cwl/PrecomputeSlide.cwl
