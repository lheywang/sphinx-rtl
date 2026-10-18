# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Build the standard VHDL parser.
# ----------------------------------------------------------------------------

# Imports
from typing import Any, Protocol
from pathlib import Path
from sphinx_rtl.models import Component
from sphinx_rtl.RTLParser.xParser import xParser
from sphinx.util import logging

import tree_sitter_vhdl as tsvhdl
from tree_sitter import Language, Parser, Query, QueryCursor

from .queries import get_queries

# Define the language
VHDL_LANGUAGE = Language(tsvhdl.language())

queries = get_queries(VHDL_LANGUAGE)

# Logger config
logger = logging.getLogger(__name__)


class VHDLParser(xParser):
    """
    Define the standard VHDL Parser model.
    Designed to be reused (can be openned only once and parse more than one file).
    """

    def __init__(self):
        """
        Init the VHDL parser for different operations.
        """

        # Init the parser, shared over all parsing passes.
        self.parser = Parser(VHDL_LANGUAGE)

    @staticmethod
    def _extract_text(node: Any, source: bytes) -> str:
        """Découpe le buffer d'octets pour récupérer le code textuel d'un nœud."""
        if node is None:
            return ""
        return source[node.start_byte : node.end_byte].decode("utf-8").strip()

    def parse(self, file: Path):
        """
        Parse the passed file as VHDL, and output the built class.
        """

        code: bytes = file.read_bytes()

        tree = self.parser.parse(code)

        # Allocate memory for the remaining elements.
        components: list[Component] = []

        # Using queries, we could fetch all elements directly
        for name, query in queries.items():
            print(f"""
-------------------
{name}
-------------------            
""")
            cursor = QueryCursor(query)
            results = []

            for index, match in cursor.matches(tree.root_node):
                if "port.ids" in match:
                    id_node = match["port.ids"][0]

                    names = [
                        self._extract_text(c, code)
                        for c in id_node.children
                        if c.type == "identifier"
                    ]
                    base_type = self._extract_text(match["port.subtype"][0], code)

                    mode_nodes = match.get("port.mode", [])
                    direction = (
                        self._extract_text(mode_nodes[0], code).lower()
                        if mode_nodes
                        else "in"
                    )

                    print(names, direction, base_type, id_node.start_point.row + 1)
