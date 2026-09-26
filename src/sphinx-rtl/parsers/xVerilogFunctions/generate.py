# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Extract all the imports from a module
# ----------------------------------------------------------------------------

# Imports
import re
import pyslang.ast as ast
import pyslang.syntax as syntax

from ...models import Module
from .utils import get_size_and_type


def build_generate(
    node: ast.GenerateBlockSymbol | ast.GenerateBlockArraySymbol, line: int
) -> Module:
    """
    Build the signal object from a passed signal node.

    Another slightly different usage of the standard procedure matching,
    """

    if node.kind == ast.SymbolKind.GenerateBlock:
        pass

    elif node.kind == ast.SymbolKind.GenerateBlockArray:
        loop: ast.GenerateBlockArraySymbol = node  # type: ignore
        entries: list[ast.GenerateBlockSymbol] = loop.entries

        if len(entries) == 0:
            # First, get the iteration count (as a CST node)
            # We assume that the iter start at 0.
            iter = str(loop.iterExpression.syntax).strip()
            end = str(loop.stopExpression.syntax).strip()

            iterator, expr = iter.split("=")
            print(iterator, expr, end)
            count = 0
        else:
            count = len(entries)

        members: list[syntax.HierarchyInstantiationSyntax] = loop.syntax.block.members
        for member in members:
            print(member.type)  # Entity name

            instances: list[syntax.HierarchicalInstanceSyntax] = member.instances
            for inst in instances:
                print(inst.connections)
                print(inst.decl.name)  # mod name

                conns: list[syntax.NamedPortConnectionSyntax] = [
                    x
                    for x in inst.connections
                    if type(x) is syntax.NamedPortConnectionSyntax
                ]

                for conn in conns:
                    print(str(conn).strip())

                # params
                # connections ... ??
                # repeat count
                # and so on...

    # Shall not end up here anyway...
    return Module()
