# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Comment transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Comment
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VHDLTransformerComment(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Comment | None:

    # Extract the content of the node
    content = ""
    line = get_line(nodes["content"][0])
    for element in nodes["content"]:
        content = content + get_text(element, source)

    # Can this comment be merged ?
    first_node = nodes["content"][0]

    # Fetch the content of the line BEFORE the comment.
    # This is used to identify if a command can be merged.
    start_byte = first_node.start_byte
    line_start_byte = source.rfind(b"\n", 0, start_byte) + 1
    prefix = source[line_start_byte:start_byte].decode("utf-8", errors="ignore")

    # If there's things before our token, we set the comment as inline.
    prefix = prefix.strip().removeprefix("--").strip()
    is_inline = bool(prefix.strip())

    # Build an object
    return Comment(line=line, content=content, merge_authorized=not is_inline)
