# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Port transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Port
from sphinx_rtl.RTLParser2.languages.utils import get_text

from .utils import get_vector


# Functions
def VHDLTransformerPort(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Port | list[Port] | None:

    # Does it have the required properties ?
    if (
        "port.ids" not in nodes
        or "port.subtype" not in nodes
        or "port.mode" not in nodes
    ):
        return None

    elements: list[tuple[int, str, str, list[str], str]] = get_vector(
        nodes["port.ids"][0],
        nodes["port.subtype"][0],
        source,
        nodes["port.init"][0] if "port.init" in nodes else None,
    )

    # Fetch the port mode
    mode = get_text(nodes["port.mode"][0], source)
    direction = "input" if mode.lower() == "in" else "output"

    # Build the object
    ports: list[Port] = []

    for element in elements:
        line, name, typ, size, init = element
        ports.append(
            Port(
                name=name,
                line=line,
                hdl_type=typ,
                hdl_size=size,
                hdl_value=init,
                direction=direction,
            )
        )

    return ports
