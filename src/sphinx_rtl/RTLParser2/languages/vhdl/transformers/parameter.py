# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Parameter transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Parameter

from .utils import get_vector


# Functions
def VHDLTransformerParameter(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Parameter | list[Parameter] | None:

    # Does it have the required properties ?
    if "param.ids" not in nodes or "param.subtype" not in nodes:
        return None

    elements: list[tuple[int, str, str, list[str], str]] = get_vector(
        nodes["param.ids"][0],
        nodes["param.subtype"][0],
        source,
        nodes["param.init"][0] if "param.init" in nodes else None,
    )

    # Build the object
    params: list[Parameter] = []
    for element in elements:
        line, name, typ, _, init = element
        params.append(Parameter(name=name, line=line, hdl_type=typ, hdl_value=init))

    return params
