# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Comment transformer
# ----------------------------------------------------------------------------

# Import
import re

from tree_sitter import Node

from sphinx_rtl.models import Comment
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VerilogTransformerComment(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Comment | None:

    # Get the content
    raw = get_text(nodes["comment"][0], source)
    text = re.sub(r"^(\/\*+|\/\/+)[!\s]*", "", raw)
    text = re.sub(r"\*+\/\s*$", "", text)

    lines = []
    for line in text.splitlines():
        cleaned_line = re.sub(r"^\s*\*(?!\*)", "", line)
        lines.append(cleaned_line.strip())

    # Get the line
    line = get_line(nodes["comment"][0])

    # Can this comment be merged ?
    first_node = nodes["comment"][0]

    # Fetch the content of the line BEFORE the comment.
    # This is used to identify if a command can be merged.
    start_byte = first_node.start_byte
    line_start_byte = source.rfind(b"\n", 0, start_byte) + 1
    prefix = source[line_start_byte:start_byte].decode("utf-8", errors="ignore")

    # If there's things before our token, we set the comment as inline.
    prefix = prefix.strip()
    is_inline = bool(prefix.strip())

    return Comment(content="\n".join(lines), line=line, merge_authorized=not is_inline)
