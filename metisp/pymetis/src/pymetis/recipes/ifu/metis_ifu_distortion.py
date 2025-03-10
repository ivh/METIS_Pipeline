"""
This file is part of the METIS Pipeline.
Copyright (C) 2024 European Southern Observatory

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import re

import cpl
from cpl.core import Msg
from typing import Dict

from pymetis.base.recipe import MetisRecipe
from pymetis.base.product import PipelineProduct
from pymetis.inputs import RawInput, SinglePipelineInput, MasterDarkInput
from pymetis.inputs.common import PinholeTableInput
from pymetis.inputs.mixins import PersistenceInputSetMixin, LinearityInputSetMixin, GainMapInputSetMixin
from pymetis.prefab.darkimage import DarkImageProcessor
from pymetis.prefab.rawimage import RawImageProcessor


class MetisIfuDistortionImpl(DarkImageProcessor):
    class InputSet(LinearityInputSetMixin, GainMapInputSetMixin, PersistenceInputSetMixin, DarkImageProcessor.InputSet):
        MasterDarkInput = MasterDarkInput

        class RawInput(RawInput):
            _tags: re.Pattern = re.compile(r"IFU_DISTORTION_RAW")

        def __init__(self, frameset: cpl.ui.FrameSet):
            super().__init__(frameset)
            self.pinhole_table = PinholeTableInput(frameset)

            self.inputs |= {self.pinhole_table}


    class ProductIfuDistortionTable(PipelineProduct):
        _tag = r"IFU_DISTORTION_TABLE"
        _level = cpl.ui.Frame.FrameLevel.FINAL
        _frame_type = cpl.ui.Frame.FrameType.TABLE

    class ProductIfuDistortionReduced(PipelineProduct):
        _tag = r"IFU_DIST_REDUCED"
        _level = cpl.ui.Frame.FrameLevel.FINAL
        _frame_type = cpl.ui.Frame.FrameType.IMAGE

    def process_images(self) -> [PipelineProduct]:
        raw_images = cpl.core.ImageList()

        for idx, frame in enumerate(self.inputset.raw.frameset):
            Msg.info(self.name, f"Loading raw image {frame.file}")

            if idx == 0:
                self.header = cpl.core.PropertyList.load(frame.file, 0)

            raw_image = cpl.core.Image.load(frame.file, extension=1)
            raw_images.append(raw_image)

        combined_image = self.combine_images(raw_images, "average")

        product_distortion = self.ProductIfuDistortionTable(self, self.header, combined_image)
        product_distortion_reduced = self.ProductIfuDistortionReduced(self, self.header, combined_image)

        return [product_distortion, product_distortion_reduced]


class MetisIfuDistortion(MetisRecipe):
    _name: str = "metis_ifu_distortion"
    _version: str = "0.1"
    _author: str = "Martin Baláž"
    _email: str = "martin.balaz@univie.ac.at"
    _synopsis: str = "Reduce raw science exposures of the IFU."
    _description: str = (
        "Currently just a skeleton prototype."
    )

    implementation_class = MetisIfuDistortionImpl
