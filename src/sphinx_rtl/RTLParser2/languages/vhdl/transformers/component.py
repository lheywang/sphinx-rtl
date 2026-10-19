# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Assign transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Component, FileInfo
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerComponent(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Component:
    print(nodes)
    return Component(FileInfo())
