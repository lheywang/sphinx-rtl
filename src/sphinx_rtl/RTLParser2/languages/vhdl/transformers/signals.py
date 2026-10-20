# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Signal transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Signal

from .utils import get_vector


# Functions
def VHDLTransformerSignal(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Signal | list[Signal] | None:
    # Does it have the required properties ?
    if "signal.ids" not in nodes or "signal.subtype" not in nodes:
        return None

    elements: list[tuple[int, str, str, list[str], str]] = get_vector(
        nodes["signal.ids"][0],
        nodes["signal.subtype"][0],
        source,
        nodes["signal.init"][0] if "signal.init" in nodes else None,
    )

    # Build the object
    signals: list[Signal] = []

    for element in elements:
        line, name, typ, size, init = element
        signals.append(
            Signal(name=name, line=line, hdl_type=typ, hdl_size=size, hdl_value=init)
        )

    return signals
