# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import copy
import pyslang.ast as ast
from pyslang import SourceManager

from ...models import Modport, Port


def build_modport(node: ast.ModportSymbol, line: int, sm: SourceManager) -> Modport:
    """
    Build the modport object from a passed modport node.

    This one is really easy to do !
    """

    # Extract basic informations
    name = node.name

    # Get the different elements
    ports: list[Port] = [Port()]
    for elem in node:

        # Build a new port
        port = copy.deepcopy(ports[-1])

        # Get default values
        if elem.name != "":
            port.name = elem.name

        # Get the direction
        match elem.direction:  # type: ignore
            case ast.ArgumentDirection.In:
                port.direction = "input"
            case ast.ArgumentDirection.Out:
                port.direction = "output"
            case ast.ArgumentDirection.InOut:
                port.direction = "inout"

        # Add line (relative to the current line.)
        current_line = sm.getLineNumber(elem.location)
        if current_line == 0:
            current_line = -1
        port.line = current_line

        # Append to the list
        ports.append(port)

    # Remove the first port (used as memory effect)
    ports = ports[1:]

    # Assemble the modport object
    return Modport(name=name, line=line, signals=ports)
