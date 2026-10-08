# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import re
import pyslang.ast as ast
import pyslang.syntax as syntax

from ...models import Signal
from .utils import get_size_and_type


def build_signal(node: ast.VariableSymbol | ast.NetSymbol, line: int) -> Signal:
    """
    Build the signal object from a passed signal node.

    Another slightly different usage of the standard procedure matching,
    """

    # Extract the name
    name = node.name.strip()
    implicit = False

    if node.kind == ast.SymbolKind.Variable:

        parent: syntax.DataDeclarationSyntax = node.syntax.parent
        unpacked_dims = (
            [str(d).strip() for d in node.syntax.dimensions]
            if hasattr(node.syntax, "dimensions")
            else []
        )

        # Make the thing cleaner
        hdl_type, hdl_size = get_size_and_type(str(parent.type).strip())

        # Add the declarator part size
        for dim in unpacked_dims:
            _, size = get_size_and_type(dim)
            if size[0] != size[1]:
                hdl_size.extend(size)

    elif node.kind == ast.SymbolKind.Net:

        parent: syntax.DataDeclarationSyntax = node.syntax.parent
        unpacked_dims = (
            node.syntax.dimensions if hasattr(node.syntax, "dimensions") else "[0:0]"
        )

        hdl_type = "logic"
        _, hdl_size = get_size_and_type(unpacked_dims)
        implicit = node.isImplicit  # type: ignore

    else:

        hdl_type = "unknown"
        hdl_size = ["0", "0"]

    # Build the output node
    return Signal(
        name=name,
        hdl_type=hdl_type,
        hdl_size=hdl_size,
        hdl_value="unknown",
        line=line,
        isImplicit=implicit,
    )
