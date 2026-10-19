# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define our custom implementation of the VHDL language.
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.RTLParser2.languages import LanguageSpec
from tree_sitter import Language
from dataclasses import dataclass

import tree_sitter_vhdl

from .queries import get_queries
from .transformers import get_transformers

# Define the class
VHDL_LANGUAGE = Language(tree_sitter_vhdl.language())


@dataclass(slots=True)
class VHDLSpecification(LanguageSpec):
    """
    Define our custom implementation of the VHDL specification.
    """

    def __post_init__(self) -> None:

        # Update the language
        self.name = "VHDLSpecification"
        self.ts_lang = VHDL_LANGUAGE
        self.extensions = ["vhd", "vhdl"]

        # Fill the queries and transformers
        if self.ts_lang is not None:
            self.ts_queries = get_queries(self.ts_lang)
            self.ts_transformers = get_transformers()
            self.ts_explore_query = "Q_ENTITY"
