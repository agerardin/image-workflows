# Goals

Typical workflows we want to support :

1/ The user wants to download datasets and convert them to a standard format for further processing.
2/ If the dataset is already described as images + stitching vectors, then we need to regenerate the stitching vector to account for the name changes, otherwise we may want to run `nist mist` or the `montage plugin`.
3/ Finally we want to assemble and build a full pyramid.

## Setup

See `INSTALL.md`

## Generate Compute Workflow

`python -m polus.plugins.workflow_generator WORKFLOW_SPEC`

Example : 

`python -m polus.plugins.workflow_generator config/process/BBBC/BBBC001_process.yaml`

## Run Workflow on Compute

Set up env variables:

COMPUTE_URL=COMPUTE_URL


run `python compute.py`. Note that you will also need to set
COMPUTE_CLIENT_ID and COMPUTE_CLIENT_SECRET env variables to appropriate values.


## Generating Workflows

## Workflow 1 - Download
This workflow implementation will be specific for each source (download) and each dataset (download and convert)
For now we have identified 3 sources : the BBBC collection, the IDR collection, and the NIST MIST reference dataset.

## Workflow 2 - Convert
This workflow implementation will be specific for each source (download) and each dataset (download and convert)
For now we have identified 3 sources : the BBBC collection, the IDR collection, and the NIST MIST reference dataset.

## Workflow 3 - Recycle or Montage/NIST_MIST
Montage will be useful for certain datasets where several images create the full region of interest
(smaller FOVs, wells on a plate etc...)
Recycle is for now a handwritten function only useful for the NIST MIST dataset. This functionality should 
be integrated in a plugin (existing or new).

## Workflow 3 - Assemble and Precompute Slide
This needs to be configured acccording to the desired output but it is mostly identical for all datasets.

## Compute
The end goal is to run those fully configured workflows with Compute.
For that we need to secure an access token with which we can claim our identity for each compute requests.

Code exists to obtain a token. In order to do so two environment variables needs to be set up :
COMPUTE_CLIENT_ID and COMPUTE_CLIENT_SECRET. Those values are used to obtain a valid access token from the auth endpoint. 

## Dataset sources

### [Broad Bioimage Benchmark Collection](https://bbbc.broadinstitute.org/) (BBBC)
Contains dataset for various experiments. The goal of this collection 
is to provide images and ground truths related to one or several tasks in
order to develop and benchmark image processing algorithms.

NOTE : Certain ground_truths are also images and will also need to be preprocess.
When running the conversion pipeline we need to identify those.

### [Image Data Resource](https://idr.openmicroscopy.org/) (IDR)
A huge diversity of different experiments.
Metadata depends on the datasets.
Directory structure as well.
Metadata are hosted on github.
Datasets are often high throughput miscroscopy so very large datasets.
