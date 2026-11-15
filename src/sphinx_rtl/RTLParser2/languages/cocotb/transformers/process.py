# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Process transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Process
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def CocotbTransformerProcess(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Process | None:

    # Is there everything for us ?
    if "name" not in nodes:
        return

    # Build the process
    proc = Process()
    proc.line = get_line(nodes["name"][0])
    proc.name = get_text(nodes["name"][0], source)

    return proc
