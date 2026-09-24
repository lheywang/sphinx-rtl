# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import re
import pyslang.ast as ast

from ...models import Assignment


def build_assignment(node: ast.ContinuousAssignSymbol, line: int) -> Assignment:
    """
    Build the assignement object from a passed assign node.
    """

    # Extract the LHS and RHS
    syntax = str(node.syntax)
    assigns = syntax.split("=", 1)

    # Alloc output
    rhs = ""
    lhs = []

    if len(assigns) > 1:
        rhs = assigns[0].strip()
        lhs = list(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_$]*\b", assigns[1]))

    # Build the output object
    return Assignment(
        target=rhs, source=lhs, isComb=False if len(lhs) == 1 else True, line=line
    )
