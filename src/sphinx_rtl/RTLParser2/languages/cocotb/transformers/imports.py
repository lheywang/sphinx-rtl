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
def CocotbTransformerImport(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Import | None:

    # Is there everything for us ?
    if "import" not in nodes:
        return

    # Build the object
    imp = Import()
    imp.line = get_line(nodes["import"][0])

    # Fetch the import target
    imp.element = [get_text(nodes["import"][0], source)]

    # Is there an alias defined ?
    if "alias" in nodes:
        imp.library = imp.name
        imp.element = [get_text(nodes["alias"][0], source)]

    return imp
