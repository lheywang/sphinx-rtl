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

        # Extract each pairs
        size_pairs = [x.strip() for x in raw_syntax[1].replace("[", "").split("]")]

        # For each pairs, append one to the port
        for size_pair in size_pairs:
            temp = size_pair.replace("::", ";;")
            bounds = [x.strip() for x in temp.split(":")]

            # If there's at least two bounds
            if len(bounds) >= 2:
                hdl_size.append(bounds[0].replace(";;", "::"))
                hdl_size.append(bounds[1].replace(";;", "::"))

    else:
        hdl_size = ["0", "0"]

    # Add the declarator part size
    for raw_dimension in unpacked_dims:

        size_pairs = [
            x.strip() for x in raw_dimension.replace("[", "").split("]") if len(x) > 0
        ]

        # Attempt to split the pairs, if fail that's a Scalar
        for size_pair in size_pairs:
            temp = size_pair.replace("::", ";;")
            bounds = [x.strip() for x in temp.split(":")]

            # scalar
            if len(bounds) == 1:
                if bounds[0].isdecimal():
                    hdl_size.append(f"{int(bounds[0].replace(";;", "::")) - 1}")
                else:
                    hdl_size.append(bounds[0].replace(";;", "::"))
                hdl_size.append("0")

            elif len(bounds) == 2:
                hdl_size.append(bounds[0].replace(";;", "::"))
                hdl_size.append(bounds[1].replace(";;", "::"))

    # Build the output node
    return Signal(
        name=name,
        hdl_type=hdl_type,
        hdl_size=hdl_size,
        hdl_value="unknown",
        line=line,
    )
