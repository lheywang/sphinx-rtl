# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.RTLParser2.languages import LanguageSpec
from tree_sitter import Language
from dataclasses import dataclass

import tree_sitter_verilog

from .queries import get_queries
from .transformers import get_transformers

# Define the class
VERILOG_LANGUAGE = Language(tree_sitter_verilog.language())


@dataclass(slots=True)
class SystemverilogSpecification(LanguageSpec):
    """
    Define our custom implementation of the VHDL specification.
    """

    def __post_init__(self) -> None:

        # Update the language
        self.name = "SystemverilogSpecification"
        self.ts_lang = VERILOG_LANGUAGE
        self.extensions = ["v", "sv", "svh"]

        # Fill the queries and transformers
        if self.ts_lang is not None:
            self.ts_queries = get_queries(self.ts_lang)
            self.ts_transformers = get_transformers()
