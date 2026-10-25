# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :
# ----------------------------------------------------------------------------

# Imports
import tree_sitter_verilog

from tree_sitter import Language
from dataclasses import dataclass

from sphinx_rtl.RTLParser2.languages import LanguageSpec
from sphinx_rtl.RTLParser2.languages.utils import get_text

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
            self.ts_explore_query = "Q_ENTITIES"
            self.ts_top_name = lambda n, c: get_text(n["entity.node"][0], c)
