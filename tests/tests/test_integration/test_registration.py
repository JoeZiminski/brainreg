import os
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from imio.load import load_any

from brainreg.cli import main as brainreg_run

test_data_dir = Path(os.getcwd()) / "tests" / "data"

brain_data_dir = test_data_dir / "brain data"
expected_niftyreg_output_dir = (
    test_data_dir / "registration_output" / platform.system()
)
# Create a directory to save test data during pytest runs
test_output_dir = test_data_dir / "test_output"
test_output_dir.mkdir(exist_ok=True)

x_pix = "40"
y_pix = "40"
z_pix = "50"

relative_tolerance = 0.01
absolute_tolerance = 10
check_less_precise_pd = 1


def test_registration_niftyreg(tmpdir):
    brainreg_args = [
        "brainreg",
        str(brain_data_dir),
        str(test_output_dir),
        "-v",
        z_pix,
        y_pix,
        x_pix,
        "--orientation",
        "psl",
        "--n-free-cpus",
        "0",
        "--atlas",
        "allen_mouse_100um",
        "-d",
        str(brain_data_dir),
    ]

    sys.argv = brainreg_args
    brainreg_run()

    # none of this testing is ideal, as results seem to vary between systems
    image_list = [
        "boundaries.tiff",
        "deformation_field_0.tiff",
        "deformation_field_1.tiff",
        "deformation_field_2.tiff",
        "downsampled.tiff",
        "downsampled_brain data.tiff",
        "downsampled_standard.tiff",
        "downsampled_standard_brain data.tiff",
        "registered_atlas.tiff",
        "registered_hemispheres.tiff",
    ]
    for image in image_list:
        are_images_equal(image, test_output_dir, expected_niftyreg_output_dir)

    if platform.system() == "Linux":
        pd.testing.assert_frame_equal(
            pd.read_csv(os.path.join(test_output_dir, "volumes.csv")),
            pd.read_csv(
                os.path.join(expected_niftyreg_output_dir, "volumes.csv")
            ),
        )


def are_images_equal(image_name, output_directory, test_output_directory):
    image = load_any(
        os.path.join(output_directory, image_name),
    )
    test_image = load_any(
        os.path.join(test_output_directory, image_name),
    )
    np.testing.assert_allclose(
        image, test_image, rtol=relative_tolerance, atol=absolute_tolerance
    )
