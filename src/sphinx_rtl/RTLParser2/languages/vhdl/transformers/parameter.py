# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Parameter transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Parameter
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerParameter(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Parameter:
    print(nodes)
    return Parameter()
