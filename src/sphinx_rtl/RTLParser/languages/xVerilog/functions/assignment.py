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

from sphinx_rtl.models import Assignment

from .utils import get_size_and_type


def build_assignment(
    node: ast.ContinuousAssignSymbol | syntax.BinaryExpressionSyntax, line: int
) -> Assignment:
    """
    Build the assignement object from a passed assign node.
    """

    # Extract the LHS and RHS
    raw = str(getattr(node, "syntax", node))
    raw = re.sub(r"^\s*assign\b\s*", "", raw)

    # Clean up the assign, this is a bit hacky but the function is well tested.
    assigns = [get_size_and_type(x)[0] for x in raw.split("=")]

    # Alloc output
    rhs = ""
    lhs = []

    if len(assigns) > 1:
        rhs = assigns[0].strip()
        lhs = list(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_$]*\b", ",".join(assigns[1:])))

    if len(lhs) == 0:
        lhs.append("'0")

    # Build the output object
    return Assignment(
        target=rhs, source=lhs, isComb=False if len(lhs) <= 1 else True, line=line
    )
