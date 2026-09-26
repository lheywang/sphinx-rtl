# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import copy
import pyslang.ast as ast
import pyslang.syntax as syntax

from ...models import Port
from .utils import get_size


def build_port(previous: Port, node: ast.PortSymbol, line: int) -> Port:
    """
    Build a port object from the passed source !

    The code is crap, I know. But, due to the slight variations between each cases,
    it's hard to efficiently move to functions the redundant code. So, it work, I won't
    touch it...
    """

    # Build a new port
    port = copy.deepcopy(previous)

    # Get default values
    if node.name != "":
        port.name = node.name

    # Get the direction
    match node.direction:
        case ast.ArgumentDirection.In:
            port.direction = "input"
        case ast.ArgumentDirection.Out:
            port.direction = "output"
        case ast.ArgumentDirection.InOut:
            port.direction = "inout"

    # Add line
    port.line = line

    # -------------------------------------------------------------------
    # PORT IS DECLARED AS ANSI
    # -------------------------------------------------------------------
    if node.isAnsiPort:

        # If Ansi port, the parameters are in the PortDeclarationSyntax:
        node_syntax: syntax.ImplicitAnsiPortSyntax = node.syntax.parent
        node_header: syntax.PortHeaderSyntax = node_syntax.header

        # We need to process the dimension of the "global" definition:
        raw_syntax = str(node_header.dataType).strip().split(" ", 1)  # type: ignore

        # Update the type
        if raw_syntax[0] != "":
            port.hdl_type = raw_syntax[0].strip()

        # Extract the dimensions
        if len(raw_syntax) > 1:
            port.hdl_size = get_size(raw_syntax[1])

        # Finally, processing the last elements (a size that may be specific to the declaration)
        node_declarator: syntax.DeclaratorSyntax = node_syntax.declarator
        port.hdl_size.extend(get_size(str(node_declarator.dimensions)))

    # -------------------------------------------------------------------
    # PORT IS DECLARED AS NON-ANSI
    # -------------------------------------------------------------------
    else:

        internal: ast.Symbol = node.internalSymbol

        decl_syntax: syntax.DeclaratorSyntax = internal.syntax
        parent: syntax.SyntaxNode = decl_syntax.parent

        # Fetch the parent node (sometimes not on the same place ...)
        data_type = None
        if hasattr(parent, "header") and hasattr(parent.header, "dataType"):  # type: ignore
            data_type = parent.header.dataType  # type: ignore
        elif hasattr(parent, "dataType"):
            data_type = parent.dataType  # type: ignore

        # Extract the dimensions
        raw_syntax = str(data_type).strip().split(" ", 1)

        # Update the type
        if raw_syntax[0].strip():
            port.hdl_type = raw_syntax[0].strip()
        else:
            port.hdl_type = "logic"

        # Extract the dimensions
        if len(raw_syntax) > 1:
            port.hdl_size = get_size(raw_syntax[1])

        # Add the declarator part size
        port.hdl_size.extend(get_size(str(decl_syntax.dimensions)))

    # Build the port
    return port


def build_interfacePort(
    previous: Port, node: ast.InterfacePortSymbol, line: int
) -> Port:
    """
    Extract the data from an Interface used as Port.
    """

    # port
    port = copy.deepcopy(previous)

    # Extract name
    name = node.name.strip()

    # Extract some infos
    raw_syntax = [
        x.strip() for x in str(node.syntax.parent).strip().split(" ") if len(x) > 0
    ]

    interface = "unknown"
    modport = "unknown"
    if len(raw_syntax) > 1 and raw_syntax[1] == name.strip():
        interface, modport = raw_syntax[0].split(".", 1)

    # Build the port we'll return :
    port.name = name
    port.direction = modport
    port.hdl_type = interface
    port.hdl_size = ["0", "0"]
    port.line = line
    return port
