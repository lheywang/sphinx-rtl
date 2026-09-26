# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast

from ...models import Function, Port
from .utils import get_size


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
            .split(" ", 1)
        )
        if len(raw_size) > 1:
            hdl_size = get_size(raw_size[1])
            hdl_type = raw_size[0].strip()
        else:
            hdl_size = get_size(raw_size[0])
            hdl_type = "logic"

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
    raw_return = [
        x.strip() for x in str(node.syntax.prototype.returnType).strip().split(" ", 1)
    ]
    print(raw_return)
    if len(raw_return) > 1:
        hdl_size = get_size(raw_return[1])
        hdl_type = raw_return[0].strip()
    else:
        if any(c.isdigit() for c in raw_return[0]):
            hdl_size = get_size(raw_return[0])
            hdl_type = "logic"
        else:
            hdl_size = ["0", "0"]
            hdl_type = raw_return[0]

    # Build the return port :
    returns: list[Port] = [
        Port(name="", direction="output", hdl_type=hdl_type, hdl_size=hdl_size)
    ]

    # Return the function
    print(Function(name=node.name, line=line, func_inputs=args, func_outputs=returns))
    return Function(name=node.name, line=line, func_inputs=args, func_outputs=returns)
