# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Port transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Port
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from sphinx_rtl.RTLParser2.languages.systemverilog.queries import (
    PORTS_ANSI_VARIABLE_Q,
    PORTS_ANSI_INTERFACE_Q,
    PORTS_ANSI_NET_Q,
    PORTS_NON_ANSI_INTERFACE_Q,
    PORTS_NON_ANSI_REF_Q,
    PORTS_NON_ANSI_INPUT_OUTPUT_Q,
    PORTS_NON_ANSI_INOUT_Q,
)

from .utils import get_size_and_type


# Functions
def VerilogTransformerPort(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Port | None:

    # Is there the root node for us ?
    if "port.node" not in nodes:
        return None

    # Initialize the output
    port = Port()
    port.line = get_line(nodes["port.node"][0])

    # Which request did match ?
    match index:

        # Non ANSI ports
        case 0:

            # Execute the second layer Query as needed.
            first = nodes["port.node"][0]
            if "port.inout" in nodes:
                for _, match in QueryCursor(PORTS_NON_ANSI_INOUT_Q).matches(first):
                    print(match)
            elif ("port.input" in nodes) or ("port.output" in nodes):
                for _, match in QueryCursor(PORTS_NON_ANSI_INPUT_OUTPUT_Q).matches(
                    first
                ):
                    print(match)
            elif "port.ref" in nodes:
                for _, match in QueryCursor(PORTS_NON_ANSI_REF_Q).matches(first):
                    print(match)
            elif "port.interface" in nodes:
                for _, match in QueryCursor(PORTS_NON_ANSI_INTERFACE_Q).matches(first):
                    print(match)

            print(nodes)

        # Ansi ports
        case 1:

            # The fetched object does miss some elements.
            if "port.name" not in nodes:
                return None

            port.name = get_text(nodes["port.name"][0], source)

            # Depending on the fetched element, run the next query.
            # We only use the first, as there's always a single match for them.
            first = nodes["port.node"][0]
            if "port.net" in nodes:
                _, match = QueryCursor(PORTS_ANSI_NET_Q).matches(first)[0]
                if match:
                    port.direction = get_text(match["direction"][0], source)
                    port.hdl_type, port.hdl_size = get_size_and_type(
                        get_text(match["type"][0], source) if "type" in match else ""
                    )
            elif "port.interface" in nodes:
                print(QueryCursor(PORTS_ANSI_INTERFACE_Q).matches(first))
                _, match = QueryCursor(PORTS_ANSI_INTERFACE_Q).matches(first)[0]
                if match:
                    print("Matched", match)
                    port.direction = get_text(match["direction"][0], source)
                    port.hdl_type, port.hdl_size = get_size_and_type(
                        get_text(match["type"][0], source)
                    )
            elif "port.var" in nodes:
                _, match = QueryCursor(PORTS_ANSI_VARIABLE_Q).matches(first)[0]
                if match:
                    port.direction = get_text(match["direction"][0], source)
                    port.hdl_type, port.hdl_size = get_size_and_type(
                        get_text(match["type"][0], source)
                    )

    print(port)

    return port
