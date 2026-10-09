# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast
import pyslang.syntax as syntax
from pyslang import SourceManager

from sphinx_rtl.models import Module, Parameter
from .utils import get_size_and_type


def build_module(node: ast.SymbolKind.UninstantiatedDef, line: int, sm: SourceManager) -> Module:  # type: ignore
    """
    Build a module from the passed informations.
    """
    # Fetch the node with a proper name (for IDE autocomplete)
    mod: ast.UninstantiatedDefSymbol = node

    # Extract the connections from the CST
    conns: list[
        syntax.NamedPortConnectionSyntax | syntax.OrderedPortConnectionSyntax
    ] = [
        x
        for x in mod.syntax.connections
        if type(x) is syntax.NamedPortConnectionSyntax
        or type(x) is syntax.OrderedPortConnectionSyntax
    ]

    # Is the instance present more than once ?
    repeat = False
    count = 1
    _, size = get_size_and_type(str(node.syntax.decl))
    if size[0] != size[1]:
        repeat = True
        count = int(size[0]) - 1

    # Extract the connections
    connections: list[tuple[str, str]] = []
    for conn, name in zip(conns, mod.portNames):
        connections.append((name.strip(), str(conn.expr).strip()))

    # Extract the parameters
    params: list[Parameter] = []
    if mod.syntax.parent.parameters is not None:
        parameters: list[
            syntax.NamedParamAssignmentSyntax | syntax.OrderedParamAssignmentSyntax
        ] = [
            x
            for x in mod.syntax.parent.parameters
            if type(x) == syntax.NamedParamAssignmentSyntax
            or type(x) == syntax.OrderedParamAssignmentSyntax
        ]
        for parameter in parameters:
            name = ""
            val = ""
            param_line = -1
            match type(parameter):
                case syntax.NamedParamAssignmentSyntax:
                    name = str(parameter.name)  # type: ignore
                    val = str(parameter.expr) if parameter.expr else ""
                case syntax.OrderedParamAssignmentSyntax:
                    val = str(parameter.expr) if parameter.expr else ""

            temp_line = sm.getLineNumber(parameter.sourceRange.start)
            if temp_line != 0:
                param_line = temp_line

            params.append(Parameter(name=name, hdl_value=val, line=param_line))

    # Build the Module
    return Module(
        name=node.name,
        entity=mod.definitionName,
        connections=connections,
        params=params,
        line=line,
        isRepeated=repeat,
        count=f"{count}",
    )
