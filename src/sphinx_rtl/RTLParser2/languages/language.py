# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the core elements of a language specification.
# ----------------------------------------------------------------------------

# Imports
from dataclasses import dataclass, field
from typing import Callable, Optional, Any
from tree_sitter import Language, Query, Node
from sphinx.util import logging
from pathlib import Path

from sphinx_rtl.models import (
    Port,
    Enum,
    Parameter,
    Structure,
    Import,
    Signal,
    Process,
    Assignment,
    Module,
    Function,
    Interface,
    Comment,
)

# Configure the logger
logger = logging.getLogger(__name__)


# Class
@dataclass(slots=True)
class LanguageSpec:
    """
    Build the specification for a single language.
    Make an heritage of it, and append your own elements !

    Fields :
        - name : The name of the language to be shown in the logs
        - extensions : The list of extensions to be used for this format
        - ts_lang : A tree-sitter language to be used.

        The following fields are only used if ts_lang is not None. That mean the language is an extension based on ts_lang.
        - ts_queries : The dict of queries for the different elements to be fetched.
        - ts_explore_query : The first query to be executed, and charged to build the top level entities.
        - ts_transformers : The dict of functions to be used to transform the result of a query into a standard element (check sphinx_rtl.models).
                            The keys must be the same as the ones in ts_queries.

        The following fields are only used is ts_lang is None. That mean the language must be parsed as a standalone tool.
        std_parser : A function where we pass the target Path, and hope for the best.

        The last fields are common, optional callbacks. Theses are called some points within the execution to perform different operations :
        - comment_transformer : Enable to transform comments before passing them to the linker.
    """

    name: str = ""
    extensions: list[str] = field(default_factory=list)
    ts_lang: Language | None = None

    # If language is not None, we'll use these as the parser.
    ts_queries: dict[str, Query] = field(default_factory=dict)
    ts_explore_query: str = ""
    ts_transformers: dict[
        str,
        Callable[
            [int, dict[str, list[Node]], bytes],
            Port
            | list[Port]
            | Enum
            | list[Enum]
            | Parameter
            | list[Parameter]
            | Structure
            | list[Structure]
            | Import
            | list[Import]
            | Signal
            | list[Signal]
            | Process
            | list[Process]
            | Assignment
            | list[Assignment]
            | Module
            | list[Module]
            | Function
            | list[Function]
            | Interface
            | list[Interface]
            | Comment
            | list[Comment],
        ],
    ] = field(default_factory=dict)
    ts_top_name: Optional[Callable[[dict[str, list[Node]], bytes], str]] = None

    # Else, let's use the default parser (does)
    std_parser: Optional[Callable[[Path], Any]] = None

    # Common definition
    comment_transformer: Optional[Callable[[list[Comment]], list[Comment]]] | None = (
        None
    )
