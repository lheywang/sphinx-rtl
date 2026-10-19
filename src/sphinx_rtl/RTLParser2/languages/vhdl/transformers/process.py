# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Process transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Process
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerProcess(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Process:
    print(nodes)
    return Process()
