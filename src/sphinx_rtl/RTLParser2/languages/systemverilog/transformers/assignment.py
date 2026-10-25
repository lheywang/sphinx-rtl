# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Assignment transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Assignment
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VerilogTransformerAssignment(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Assignment | None:

    print(nodes)

    return None
