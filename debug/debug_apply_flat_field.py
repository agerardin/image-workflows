from polus.plugins.regression.basic_flatfield_estimation.__main__ import (
    main as basic_flatfield_estimation_main,
)

from polus.plugins.transforms.images.apply_flatfield.__main__ import (
    main as apply_flatfield_main,
)

from pathlib import Path

fovs_dir = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/inpDirBasicFlatfieldEstimation")
ff_dir = Path("/Users/antoinegerardin/Documents/projects/polus-pipelines/ffDirApplyFlatfield")
fovs_pattern = "d1_x00_y03_p{p:dd}_c{c:d}.ome.tif"
ff_group_by = "c"

ff_pattern = "d1_x00_y03_p0\\(0-5\\)_c{c:d}_darkfield.ome.tif"
df_pattern = "d1_x00_y03_p0\\(0-5\\)_c{c:d}_flatfield.ome.tif"
fovs_corrected_dir = Path("inpDirImageAssembler")



if __name__ == "__main__":
    basic_flatfield_estimation_main(
        inp_dir=fovs_dir,
        out_dir=ff_dir,
        pattern=fovs_pattern,
        group_by=ff_group_by,
        get_darkfield=True,
        preview=False,
    )

    apply_flatfield_main(
        img_dir=fovs_dir,
        img_pattern=fovs_pattern,
        ff_dir=ff_dir,
        ff_pattern=ff_pattern,
        df_pattern=df_pattern,
        out_dir=fovs_corrected_dir,
        preview=False,
    )

