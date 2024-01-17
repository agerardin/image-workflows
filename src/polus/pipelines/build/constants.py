"""This file contains all constants used in the module.

In particular, all staging directories are defined here.
"""

from pathlib import Path
import os

# We only target the argo-driver
DRIVER = "argo"

# Set to True to modify wic-generated workflow to align with Compute restrictions regarding cwl.
COMPUTE_COMPATIBILITY = True

# Current Working Directory
WORKING_DIR = Path(os.getcwd()).resolve()  # preprend to all paths to create all staging directories.

# where to create CLT for the WIC API
CWL_PATH = WORKING_DIR / Path("cwl")
Path(CWL_PATH).mkdir(exist_ok=True)

# staging area for wic
WIC_PATH = WORKING_DIR / Path("wic")
Path(WIC_PATH).mkdir(exist_ok=True)

# where to create compute workflow
COMPUTE_SPEC_PATH = WORKING_DIR / Path("compute")
Path(COMPUTE_SPEC_PATH).mkdir(exist_ok=True)