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
from .utils import get_size


def build_signal(node: ast.VariableSymbol | ast.NetSymbol, line: int) -> Signal:
    """
    Build the signal object from a passed signal node.

    Another slightly different usage of the standard procedure matching,
    """

    # Extract the name
    name = node.name.strip()

    parent: syntax.DataDeclarationSyntax = node.syntax.parent
    unpacked_dims = (
        [str(d).strip() for d in node.syntax.dimensions]
        if hasattr(node.syntax, "dimensions")
        else []
    )

    # Make the thing cleaner
    clean_type = re.sub(
        r"/\*.*?\*/|//.*", "", str(parent.type), flags=re.DOTALL
    ).strip()

    # Extract the dimensions
    raw_syntax = clean_type.strip().split(" ", 1)

    # Update the type
    hdl_type = "none"
    if raw_syntax[0].strip():
        hdl_type = raw_syntax[0].strip()
    else:
        hdl_type = "logic"

    # Clear the list
    hdl_size = []

    # Extract the dimensions
    if len(raw_syntax) > 1:
        hdl_size = get_size(raw_syntax[1])

    # Add the declarator part size
    hdl_size.extend(get_size(str(unpacked_dims)))

    # Build the output node
    return Signal(
        name=name,
        hdl_type=hdl_type,
        hdl_size=hdl_size,
        hdl_value="unknown",
        line=line,
    )
