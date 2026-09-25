# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast

from ...models import Function, Port


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

        default_val = ""
        if argument.defaultValue:
            default_val = str(argument.defaultValue).strip()

        args.append(
            Port(
                name=argument.name,
                direction=dir_str,
                hdl_type=argument.type.name,
                hdl_value=default_val,
            )
        )

        # Miss the size!!! --> Utility : extract size

    print(args)

    ret_type = "" if node.returnType is not None else node.returnType.name  # type: ignore
    returns: list[Port] = []

    # Return the function
    print(Function(name=node.name, line=line, func_inputs=args, func_outputs=returns))
    return Function(name=node.name, line=line, func_inputs=args, func_outputs=returns)
