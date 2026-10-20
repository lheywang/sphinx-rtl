# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Import transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Import
from sphinx_rtl.RTLParser2.languages.utils import get_text


# Functions
def VHDLTransformerImport(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Import | None:

    # Which request did we got ?
    keys = nodes.keys()

    if "import.lib" in keys:
        lib = nodes["import.lib"]
        return Import(library=get_text(lib[0], source))

    if "import.use" in keys:
        use = nodes["import.use"]
        raw = get_text(use[0], source)

        lib, *raw = raw.split(".")
        if len(raw) > 1:
            raw = [raw[0]]

        return Import(library=lib, element=raw)

    return Import()
