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
from .utils import get_size_and_type


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

        port.hdl_type, port.hdl_size = get_size_and_type(
            str(node_header.dataType).strip()  # type: ignore
        )

        # Finally, processing the last elements (a size that may be specific to the declaration)
        for dim in node_syntax.declarator.dimensions:
            _, size = get_size_and_type(dim)
            if size[0] != size[1]:
                port.hdl_size.extend(size)

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

        port.hdl_type, port.hdl_size = get_size_and_type(str(data_type))

        # Add the declarator part size
        for dim in decl_syntax.dimensions:
            _, size = get_size_and_type(dim)
            if size[0] != size[1]:
                port.hdl_size.extend(size)

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
    raw_line = str(node.syntax.parent).splitlines()[-1]
    raw_syntax = [x.strip() for x in str(raw_line).strip().split(" ") if len(x) > 0]

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
    port.group = ""
    port.pair = ""
    return port
