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

import cpl
from cpl.core import Msg
from typing import Dict

from pymetis.base import MetisRecipe, MetisRecipeImpl
from pymetis.inputs import PipelineInput
from pymetis.base.product import PipelineProduct


class MetisIfuPostprocessImpl(MetisRecipeImpl):
    @property
    def detector_name(self) -> str | None:
        return "2RG"

    class Input(PipelineInput):
        tag_sci_cube_calibrated = "IFU_SCI_CUBE_CALIBRATED"
        detector_name = '2RG'

        def __init__(self, frameset: cpl.ui.FrameSet):
            self.sci_cube_calibrated: cpl.ui.Frame | None = None
            super().__init__(frameset)

        def categorize_frame(self, frame: cpl.ui.Frame) -> None:
            match frame.tag:
                case self.tag_sci_cube_calibrated:
                    frame.group = cpl.ui.Frame.FrameGroup.RAW # TODO What group is this really?
                    self.sci_cube_calibrated = self._override_with_warning(self.sci_cube_calibrated, frame,
                                                                           origin=self.__class__.__qualname__,
                                                                           title="sci cube calibrated")
                    Msg.debug(self.__class__.__qualname__, f"Got sci cube calibrated frame: {frame.file}.")
                case _:
                    super().categorize_frame(frame)

        def verify(self) -> None:
            pass

    class ProductSciCoadd(PipelineProduct):
        category = rf"IFU_SCI_COADD"

    def process_images(self) -> Dict[str, PipelineProduct]:
        # self.determine_output_grid()
        # self.resample_cubes()
        # self.coadd_cubes()

        header = cpl.core.PropertyList.load(self.input.sci_cube_calibrated.file, 0)
        coadded_image = cpl.core.Image()

        self.products = {
            'IFU_SCI_COADD': self.ProductSciCoadd(self, header, coadded_image, detector_name=self.detector_name),
        }
        return self.products


class MetisIfuPostprocess(MetisRecipe):
    _name = "metis_ifu_postprocess"
    _version = "0.1"
    _author = "Martin Baláž"
    _email = "martin.balaz@univie.ac.at"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Calibrate IFU science data"
    _description = (
        "Currently just a skeleton prototype."
    )

    parameters = cpl.ui.ParameterList([])
    implementation_class = MetisIfuPostprocessImpl
