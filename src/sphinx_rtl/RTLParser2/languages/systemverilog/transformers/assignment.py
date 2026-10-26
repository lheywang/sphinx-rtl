# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Assignment transformer
# ----------------------------------------------------------------------------

# Import
import re

from tree_sitter import Node

from sphinx_rtl.models import Assignment
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VerilogTransformerAssignment(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Assignment | None:

    # Is there everything for us ?
    if (
        ("assign.node" not in nodes)
        or ("assign.target" not in nodes)
        or ("assign.source" not in nodes)
    ):
        return None

    # Build the object
    assign = Assignment()

    assign.line = get_line(nodes["assign.node"][0])
    assign.target = get_text(nodes["assign.target"][0], source)
    assign.source = re.findall(
        r"\b[a-zA-Z_]\w*\b",
        re.sub(r"\[[^\]]*\]", "", get_text(nodes["assign.source"][0], source)).strip(),
    )
    assign.isComb = len(assign.source) > 1

    return None
