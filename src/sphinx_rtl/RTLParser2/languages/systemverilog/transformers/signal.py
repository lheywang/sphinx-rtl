# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Signal transformer
# ----------------------------------------------------------------------------

# Import
from copy import deepcopy

from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Signal
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from sphinx_rtl.RTLParser2.languages.systemverilog.queries import SIGNALS_NAME_Q

from .utils import get_size_and_type

# Constants
DIM_KINDS = {
    "unpacked_dimension",
    "unsized_dimension",
    "associative_dimension",
    "queue_dimension",
}


# Functions
def VerilogTransformerSignal(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Signal | list[Signal] | None:

    # Is there everything for us ?
    if ("signal.node" not in nodes) or ("signal.names" not in nodes):
        return None

    # Extract first elements
    node = nodes["signal.node"][0]
    names = nodes["signal.names"][0]

    # Build the signal
    signal = Signal()
    signal.line = get_line(node)

    signals = []
    last_type = ""
    last_size = []
    for _, match in QueryCursor(SIGNALS_NAME_Q).matches(names):
        temp = deepcopy(signal)

        # Add elements
        temp.name = get_text(match["name"][0], source) if "name" in match else ""

        # Sometimes the type may be placed on different elements...
        # Combine them before calling our function.
        full_type = ""
        if "signal.kind" in nodes:
            full_type += get_text(nodes["signal.kind"][0], source)
        if "signal.type" in nodes:
            full_type += get_text(nodes["signal.type"][0], source) + " "

        temp.hdl_type, temp.hdl_size = get_size_and_type(full_type)

        # Update accordingly to the spec the port, if declared in a single line.
        if temp.hdl_type == "":
            temp.hdl_type = last_type
        else:
            last_type = temp.hdl_type

        if temp.hdl_size == "":
            temp.hdl_size = last_size
        else:
            last_size = temp.hdl_size

        # Is there any dimension mails ?
        dims = [
            get_text(ch, source)
            for ch in match["decl"][0].named_children
            if ch.type in DIM_KINDS
        ]

        _, sizes = get_size_and_type("".join(dims))
        if sizes[0] != sizes[1]:
            temp.hdl_size.extend(sizes)

        # Add the parameter to the list
        signals.append(temp)

    return signals
