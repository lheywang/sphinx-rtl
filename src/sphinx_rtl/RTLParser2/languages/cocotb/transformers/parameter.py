# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Parameter transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Parameter
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def CocotbTransformerParameter(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Parameter | None:

    # Is there everything for us ?
    if "name" not in nodes:
        return

    # Extract the elements
    param = Parameter()
    param.line = get_line(nodes["name"][0])
    param.name = get_text(nodes["name"][0], source)

    # Additional fields
    if "type" in nodes:
        param.hdl_type = get_text(nodes["type"][0], source)
    if "value" in nodes:
        param.hdl_value = get_text(nodes["value"][0], source)

    return param
