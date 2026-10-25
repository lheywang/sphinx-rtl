# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Interface transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Interface
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VerilogTransformerInterface(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Interface | None:

    print(nodes)

    return None
