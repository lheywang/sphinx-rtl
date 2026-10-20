# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Comment transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Comment
from sphinx_rtl.RTLParser2.languages.utils import get_text


# Functions
def VHDLTransformerComment(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Comment | None:

    # Extract the content of the node
    content = ""
    line = -1
    for element in nodes["content"]:
        content = content + get_text(element, source)
        line = element.start_point[0] - 1

    # Is the comment useful ?
    if not any(c.isalnum() for c in content):
        return None

    # Build an object
    return Comment(line=line, content=content)
