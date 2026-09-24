# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast

from ...models import Parameter


def build_parameter(node: ast.ParameterSymbol, line: int) -> Parameter:
    """
    Build the parameter object from a passed parameter node.

    This one is really easy to do !
    """

    return Parameter(
        name=str(node.name),
        hdl_type=str(node.type),
        hdl_value=str(node.value),
        line=line,
    )
