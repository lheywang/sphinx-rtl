# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Parameter transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Enum, Structure
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerType(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Enum | Structure:
    print(nodes)
    return Enum()
