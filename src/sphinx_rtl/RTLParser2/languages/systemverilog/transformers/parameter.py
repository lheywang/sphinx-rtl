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

from sphinx_rtl.RTLParser2.languages.systemverilog.queries import PARAMS_ELEMENTS_Q

from .utils import get_size_and_type


# Functions
def VerilogTransformerParameter(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Parameter | None:

    # Is there everything for us ?
    if ("parameter.node" not in nodes) or ("parameter.elements" not in nodes):
        return None

    # Allocate the object for us
    param = Parameter()
    param.line = get_line(nodes["parameter.node"][0])

    # We can run the second query directly
    _, match = QueryCursor(PARAMS_ELEMENTS_Q).matches(nodes["parameter.node"][0])[0]
    if match:
        param.name = (
            get_text(match.get("parameter.identifier")[0], source)  # type: ignore
            if "parameter.identifier" in match
            else ""
        )
        param.hdl_type, _ = get_size_and_type(
            get_text(match.get("parameter.type")[0], source)  # type: ignore
            if "parameter.type" in match
            else ""
        )
        param.hdl_value = (
            get_text(match.get("parameter.value")[0], source)  # type: ignore
            if "parameter.value" in match
            else ""
        )

    # Is this a LOCALPARAM ?
    if nodes["parameter.node"][0].type == "local_parameter_declaration":
        param.constant = True

    return param
