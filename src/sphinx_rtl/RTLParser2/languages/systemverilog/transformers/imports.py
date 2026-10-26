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

    # Is there all we need ?
    if (
        ("import" not in nodes)
        or ("import.identifier" not in nodes)
        or ("import.element" not in nodes)
    ):
        return None

    # Build the output object
    imp = Import()

    # Fill the object
    imp.line = get_line(nodes["import"][0])
    imp.library = get_text(nodes["import.identifier"][0], source)
    imp.element = [get_text(nodes["import.element"][0], source)]

    return imp
