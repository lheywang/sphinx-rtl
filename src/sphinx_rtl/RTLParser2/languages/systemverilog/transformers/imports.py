# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Comment transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Import
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VerilogTransformerImport(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Import | None:

    print(nodes)

    return None
