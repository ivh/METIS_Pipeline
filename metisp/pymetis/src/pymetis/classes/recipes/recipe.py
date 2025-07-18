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

import inspect
import re
from typing import Dict, Any

import cpl

from pymetis.classes.products import PipelineProduct
from pymetis.classes.recipes.impl import MetisRecipeImpl
from pymetis.classes.inputs import PipelineInput


class MetisRecipe(cpl.ui.PyRecipe):
    """
        The abstract base class for all METIS recipes.
        In an ideal world it would also be abstract (derived from ABC, or metaclass=abc.ABCMeta),
        but `pyesorex` tries to instantiate all recipes it finds and would crash if it were an abstract class.

        The underscored _fields must be present but should be overwritten
        by every child class (`pyesorex` actually checks for their presence).
    """

    # Seven mandatory attributes follow. These are required by pyesorex and not negotiable.
    # Some of them do not have to be overwritten as they are always the same.
    _name: str = "metis_abstract_base"
    _version: str = "0.0.1"
    _author: str = "METIS PIP team, A*"
    _email: str = "astar.vienna@univie.ac.at"                    # ToDo is this a sensible default?
    _copyright: str = "GPL-3.0-or-later"                         # I guess we are using the same copyright everywhere
    _synopsis: str = "Abstract-like base class for METIS recipes"
    _description: str = ("This class serves as the base class for all METIS recipes."
                         "Bonus points if it is not visible from pyesorex.")

    # More internal attributes follow. These are **not** required by pyesorex and are specific to METIS / A*.
    _matched_keywords: set[str] = set()
    _algorithm: str = None                                      # Verbal description of the algorithm

    # By default, a recipe does not have any parameters.
    parameters: cpl.ui.ParameterList = cpl.ui.ParameterList([])
    # Default implementation class. This will not work, because it is abstract, but this is an abstract class too.
    implementation_class: type[MetisRecipeImpl] = MetisRecipeImpl

    def __init__(self):
        super().__init__()
        # Build a fancy description from attributes
        self._description: str = self._build_description()
        self.implementation: MetisRecipeImpl | None = None

    def run(self, frameset: cpl.ui.FrameSet, settings: Dict[str, Any]) -> cpl.ui.FrameSet:
        """
        The main method, as required by PyCPL.
        Instantiates the decoupled implementation, fills it with supplied frameset,
        optionally promotes the class to the proper child class and then runs it.
        """
        self.implementation = self.implementation_class(self, frameset, settings)
        return self.implementation.run()

    def _list_inputs(self) -> list[PipelineInput]:
        return inspect.getmembers(self.implementation_class.InputSet,
                                  lambda x: inspect.isclass(x) and issubclass(x, PipelineInput))

    def _list_products(self) -> list[str, PipelineProduct]:
        return inspect.getmembers(self.implementation_class,
                                  lambda x: inspect.isclass(x) and issubclass(x, PipelineProduct))

    @staticmethod
    def _format_spacing(text: str, title: str, offset: int = 4) -> str:
        fix_spacing = re.compile(r'\n\s*')
        fix_first_space = re.compile(r'^\s*')

        return fix_spacing.sub('\n' + ' ' * offset, fix_first_space.sub(' ' * offset, text)) \
            if text is not None else f'<no {title} defined>'

    def _build_description(self) -> str:
        """
        Automatically build the `description` attribute from available attributes.
        This should only depend on the class, never on an instance.
        """
        if self._matched_keywords is None:
            matched_keywords = '<not defined>'
        elif len(self._matched_keywords) == 0:
            matched_keywords = '(none)'
        else:
            matched_keywords = '\n    '.join(self._matched_keywords)

        inputs = '\n'.join(sorted([input_type.description_line() for (_, input_type) in self._list_inputs()]))
        products = '\n'.join(sorted([product_type.description_line() for (_, product_type) in self._list_products()]))
        description = self._format_spacing(self._description, 'description', 2)
        algorithm = self._format_spacing(self._algorithm, 'algorithm', 4)

        return \
            f"""{self.synopsis}\n\n{description}

  Matched keywords
    {matched_keywords}
  Inputs\n{inputs}
  Outputs\n{products}
  Algorithm\n{algorithm}
"""

    @property
    def algorithm(self):
        return self._algorithm
