# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Comment transformer
# ----------------------------------------------------------------------------

# Import
import textwrap

from tree_sitter import Node

from sphinx_rtl.models import Comment
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def CocotbTransformerComment(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Comment | None:

    # Is there a comment within it ?
    if "comment" not in nodes:
        return

    # Fetch the content of the comment
    comment = Comment()
    comment.content = get_text(nodes["comment"][0], source)
    comment.line = get_line(nodes["comment"][0])

    # Cleanup the standard syntax
    comment.content = textwrap.dedent(comment.content.strip("\"'")).strip()
    comment.content = comment.content.lstrip("#").strip()

    return comment
