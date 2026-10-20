# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Generate transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Function
from sphinx_rtl.RTLParser2.languages.utils import get_text


# Functions
def VHDLTransformerGenerate(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Function:
    print(nodes)
    return Function()
