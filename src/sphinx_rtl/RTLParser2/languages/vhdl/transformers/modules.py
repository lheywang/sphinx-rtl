# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Module transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Module
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerModule(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Module:
    print(nodes)
    return Module()
