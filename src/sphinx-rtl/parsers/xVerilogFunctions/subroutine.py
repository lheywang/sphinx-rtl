# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast

from ...models import Function, Port
from .utils import get_size_and_type


def build_function(node: ast.SubroutineSymbol, line: int = -1) -> Function:
    """
    Build a function from the passed node.
    """

    # Extract the arguments
    args: list[Port] = []
    arguments: list[ast.FormalArgumentSymbol] = node.arguments
    for argument in arguments:

        # Get the direction
        dir_str = ""
        match argument.direction:
            case ast.ArgumentDirection.In:
                dir_str = "input"
            case ast.ArgumentDirection.Out:
                dir_str = "output"
            case ast.ArgumentDirection.InOut:
                dir_str = "inout"

        # Get the port value
        default_val = ""
        if argument.defaultValue:
            default_val = str(argument.defaultValue).strip()

        # Get the size and type
        raw_size = (
            str(argument.syntax.parent)
            .replace(dir_str, "")
            .replace(argument.name, "")
            .strip()
        )

        hdl_type, hdl_size = get_size_and_type(raw_size)

        args.append(
            Port(
                name=argument.name,
                direction=dir_str,
                hdl_type=hdl_type,
                hdl_value=default_val,
                hdl_size=hdl_size,
            )
        )

    # Fetch the type of return
    hdl_type, hdl_size = get_size_and_type(str(node.syntax.prototype.returnType))

    # Build the return port :
    returns: list[Port] = [
        Port(name="", direction="output", hdl_type=hdl_type, hdl_size=hdl_size)
    ]

    # Return the function
    return Function(name=node.name, line=line, func_inputs=args, func_outputs=returns)
