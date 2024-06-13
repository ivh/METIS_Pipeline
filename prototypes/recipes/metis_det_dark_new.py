from typing import Any, Dict

from cpl import core
from cpl import ui
from cpl import dfs
from cpl.core import Msg

import sys
sys.path.append('.')
__package__ = 'prototypes.recipes'

from .base import MetisRecipe


class MetisDetDarkNew(MetisRecipe):
    # Fill in recipe information
    _name = "metis_det_dark_new"
    _version = "0.1"
    _author = "Kieran Chi-Hung Hugo Martin"
    _email = "hugo@buddelmeijer.nl"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Create master dark"
    _description = (
        "Prototype to create a METIS Masterdark."
    )

    # The recipe will have a single enumeration type parameter, which allows the
    # user to select the frame combination method.
    parameters = ui.ParameterList([
        ui.ParameterEnum(
           name="metis_det_dark.stacking.method",
           context="metis_det_dark",
           description="Name of the method used to combine the input images",
           default="average",
           alternatives=("add", "average", "median"),
        ),
    ])

    # TODO: Detect detector
    output_file = "MASTER_DARK_2RG.fits"

    def __init__(self) -> None:
        super().__init__()

    def load_input(self, frameset) -> ui.FrameSet:
        """ Go through the list of input frames, check the tag and act accordingly """

        for frame in frameset:
            # TODO: N and GEO
            if frame.tag == "DARK_LM_RAW":
                frame.group = ui.Frame.FrameGroup.RAW
                self.raw_frames.append(frame)
                Msg.debug(self.name, f"Got raw frame: {frame.file}.")
            else:
                Msg.warning(
                    self.name,
                    f"Got frame {frame.file!r} with unexpected tag {frame.tag!r}, ignoring.",
                )

        # For demonstration purposes we raise an exception here. Real world
        # recipes should rather print a message (also to have it in the log file)
        # and exit gracefully.
        if len(self.raw_frames) == 0:
            raise core.DataNotFoundError("No raw frames in frameset.")

    def filter_raw_images(self):
        for idx, frame in enumerate(self.raw_frames):
            Msg.info(self.name, f"Processing {frame.file!r}...")

            if idx == 0:
                self.header = core.PropertyList.load(frame.file, 0)

            Msg.debug(self.name, "Loading image.")
            raw_image = core.Image.load(frame.file, extension=1)

            # Insert the processed image in an image list. Of course
            # there is also an append() method available.
            self.raw_images.insert(idx, raw_image)

    def process_images(self) -> ui.FrameSet:

        # By default images are loaded as Python float data. Raw image
        # data which is usually represented as 2-byte integer data in a
        # FITS file is converted on the fly when an image is loaded from
        # a file. It is however also possible to load images without
        # performing this conversion.


        # Flat field preparation: subtract bias and normalize it to median 1
        # Msg.info(self.name, "Preparing flat field")
        # if flat_image:
        #     if bias_image:
        #         flat_image.subtract(bias_image)
        #     median = flat_image.get_median()
        #     flat_image.divide_scalar(median)


        # Combine the images in the image list using the image stacking
        # option requested by the user.
        method = self.parameters["metis_det_dark.stacking.method"].value
        Msg.info(self.name, f"Combining images using method {method!r}")

        self.combined_image = None
        # TODO: preprocessing steps like persistence correction / nonlinearity (or not)
        processed_images = self.raw_images
        if method == "add":
            for idx, image in enumerate(processed_images):
                if idx == 0:
                    self.combined_image = image
                else:
                    self.combined_image.add(image)
        elif method == "average":
            self.combined_image = processed_images.collapse_create()
        elif method == "median":
            self.combined_image = processed_images.collapse_median_create()
        else:
            Msg.error(
                self.name,
                f"Got unknown stacking method {method!r}. Stopping right here!",
            )
            # Since we did not create a product we need to return an empty
            # ui.FrameSet object. The result frameset product_frames will do,
            # it is still empty here!
            return self.product_frames

        # Save the result image as a standard pipeline product file

    def add_product_properties(self) -> None:
        # Create property list specifying the product tag of the processed image
        self.product_properties.append(
            # TODO: Other detectors
            core.Property("ESO PRO CATG", core.Type.STRING, r"MASTER_DARK_2RG")
        )

    def save_product(self) -> ui.FrameSet:
        """ Register the created product """
        Msg.info(self.name, f"Saving product file as {self.output_file!r}.")
        dfs.save_image(
            self.frameset,
            self.parameters,
            self.frameset,
            self.combined_image,
            self.name,
            self.product_properties,
            f"demo/{self.version!r}",
            self.output_file,
            header=self.header,
        )

        self.product_frames.append(
            ui.Frame(
                file=self.output_file,
                tag="MASTER_DARK_2RG",
                group=ui.Frame.FrameGroup.PRODUCT,
                level=ui.Frame.FrameLevel.FINAL,
                frameType=ui.Frame.FrameType.IMAGE,
            )
        )