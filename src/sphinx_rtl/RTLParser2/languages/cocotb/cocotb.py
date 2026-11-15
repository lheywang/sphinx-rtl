# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :
# ----------------------------------------------------------------------------

# Imports
import tree_sitter_python

from tree_sitter import Language
from dataclasses import dataclass
from pathlib import Path

from sphinx_rtl.RTLParser2.languages import LanguageSpec
from sphinx_rtl.RTLParser2.languages.utils import get_text

from .queries import get_queries
from .transformers import get_transformers

from sphinx_rtl.RTLParser2.languages.callbacks import comment_transformer

# Define the class
PYTHON_LANGUAGE = Language(tree_sitter_python.language())


@dataclass(slots=True)
class CocotbSpecification(LanguageSpec):
    """
    Define our custom implementation of the Cocotb specification.
    """

    def __post_init__(self) -> None:

        # Update the language
        self.name = "CocotbSpecification"
        self.ts_lang = PYTHON_LANGUAGE
        self.extensions = ["py"]
        self.lang_name = "python"
        self.render_type = "testbench"

        # Fill the queries and transformers
        if self.ts_lang is not None:
            self.ts_queries = get_queries(self.ts_lang)
            self.ts_transformers = get_transformers()
            self.ts_explore_query = "Q_ENTITIES"

            # This mock function use the file name as the entity name.
            # This ensure two things :
            # - The entity will cover ALL the file, and therefore include every statement within it.
            # - the name will remain coherent with the user intents.
            self.ts_top_name = lambda n, c, f: f.name.removesuffix(f.suffix)

        # Update the callbacks
        self.comment_transformer = comment_transformer
