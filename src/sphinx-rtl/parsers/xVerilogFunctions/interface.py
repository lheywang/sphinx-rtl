# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast

from ...models import Interface


def build_interface(node: ast.InstanceSymbol, line: int) -> Interface:
    """
    Build an interface from the passed node.
    """
    body: ast.InstanceBodySymbol = node.body
    print(body.definition)
    print(body.portList)
    print(body.parameters)
