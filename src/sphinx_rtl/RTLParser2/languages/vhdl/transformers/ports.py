# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Port transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Port
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerPort(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Port:
    print(nodes)
    return Port()
