# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Signal transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Signal
from sphinx_rtl.RTLParser2.languages import get_text


# Functions
def VHDLTransformerSignal(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Signal:
    print(nodes)
    return Signal()
