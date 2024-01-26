from pathlib import Path
from python_on_whales import docker
import random

fovs_dir = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/inpDirBasicFlatfieldEstimation")
ff_dir = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/ffDirApplyFlatfield")
fovs_pattern = "d1_x00_y03_p{p:dd}_c{c:d}.ome.tif"
ff_group_by = "c"

container_name = f"polus{random.randint(10, 99)}"
container_image = "polusai/basic-flatfield-estimation-plugin:2.1.0"

mounts = [
    [f"type=bind,source={fovs_dir},target=/inpDir,readonly"],
    [f"type=bind,source={ff_dir},target=/outDir"]
    ]


args = [
    f"--inpDir /inpDir",
    f"--outDir /outDir",
    f"--filePattern {fovs_pattern}",
    f"--groupBy {ff_group_by}",
    f"--getDarkfield True"
]

docker.run(container_image, args, name= container_name, mounts=mounts, remove=True)