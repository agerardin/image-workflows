# Goal

- Generate cwl workflows that can run on compute as pipelines.
- Submit pipelines to a compute instance for execution.

## Setup

We use wic to generate cwl workflows.

`pip install .`

## Generate Compute Pipeline

`python -m polus.pipeline.build PATH/TO/WORKFLOW_SPEC`

Example :

`python -m polus.pipelines.build config/process/BBBC/BBBC001_process.yaml`

## Run Pipeline on Compute

Set up env variables:

COMPUTE_URL # url of the compute api
TOKEN_URL # authentication endpoint
COMPUTE_CLIENT_ID, COMPUTE_CLIENT_SECRET

`python -m polus.pipelines.submit PATH/TO/COMPUTE_PIPELINE`

Example:

`python -m polus.pipelines.submit compute/viz_workflow_BBBC001.json`

## Generating Workflows

Typical workflows we want to support :

1. The user wants to download datasets and convert them to a standard format for further processing.
2. If the dataset is already described as images + stitching vectors, then we need to regenerate the stitching vector to account for the name changes, otherwise we may want to run `nist mist` or the `montage plugin`.
3. Finally we want to assemble and build a full pyramid.

### Workflow 1 - BBBCDownload
This workflow implementation will be specific for each data source.
For now we have identified 3 sources : the BBBC collection, the IDR collection, and the NIST MIST reference dataset.

### Workflow 2 - Process : FilRenaming / OmeConverter / Montage / ImageAssembler / PrecomputeSlide
Montage will be useful for certain datasets where several images create the full region of interest (wells on a plate etc...)
Recycle is for now a handwritten function only useful for the NIST MIST dataset. This functionality should
be integrated in a plugin (existing or new).

## Compute
The end goal is to run those fully configured workflows with Compute.

For that we need to secure an access token with which we can claim our identity for each compute requests.
There are several ways to obtain tokens, that should then referenced in an environment variable ACCESS_TOKEN.
See the `env-stub` file in repository root.

Token can also be obtained programmatically by registered developers. In order to do so two environment variables needs to be set up :
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
