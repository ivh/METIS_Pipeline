import cpl
from cpl.core import Msg
from typing import Dict

from pymetis.base.impl import MetisRecipe, MetisRecipeImpl
from pymetis.base.input import RecipeInput
from pymetis.base.product import PipelineProduct


class MetisIfuTelluricImpl(MetisRecipeImpl):
    @property
    def detector_name(self) -> str | None:
        return "2RG"

    class Input(RecipeInput):
        tags_combined = ["IFU_SCI_COMBINED", "IFU_STD_COMBINED"]
        detector_name = '2RG'

        def __init__(self, frameset: cpl.ui.FrameSet):
            self.combined: cpl.ui.Frame | None = None
            super().__init__(frameset)

        def categorize_frame(self, frame: cpl.ui.Frame) -> None:
            if frame.tag in self.tags_combined:
                frame.group = cpl.ui.Frame.FrameGroup.RAW # TODO What group is this really?
                self.combined = self._override_with_warning(self.combined, frame,
                                                            origin=self.__class__.__qualname__,
                                                            title="combined")
                Msg.debug(self.__class__.__qualname__, f"Got IFU science combined frame: {frame.file}.")
            else:
                super().categorize_frame(frame)

        def verify(self) -> None:
            pass

    class ProductSciReduced1D(PipelineProduct):
        category = rf"IFU_SCI_REDUCED_1D"

    class ProductIfuTelluric(PipelineProduct):
        category = "IFU_TELLURIC"

    class ProductFluxcalTab(PipelineProduct):
        category = "FLUXCAL_TAB"

    def process_images(self) -> Dict[str, PipelineProduct]:
        # self.correct_telluric()
        # self.apply_fluxcal()

        self.products = {
            product.category: product()
            for product in [self.ProductSciReduced1D, self.ProductIfuTelluric, self.ProductFluxcalTab]
        }
        return self.products


class MetisIfuTelluric(MetisRecipe):
    _name = "metis_ifu_telluric"
    _version = "0.1"
    _author = "Martin Baláž"
    _email = "martin.balaz@univie.ac.at"
    _copyright = "GPL-3.0-or-later"
    _synopsis = "Derive telluric absorption correction and optionally flux calibration"
    _description = (
        "Currently just a skeleton prototype."
    )

    parameters = cpl.ui.ParameterList([])
    implementation_class = MetisIfuTelluricImpl