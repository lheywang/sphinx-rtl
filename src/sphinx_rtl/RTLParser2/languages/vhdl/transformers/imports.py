# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Import transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Import
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerImport(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Import:
    print(nodes)
    return Import()
