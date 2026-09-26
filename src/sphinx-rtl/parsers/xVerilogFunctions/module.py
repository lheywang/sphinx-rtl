# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast
import pyslang.syntax as syntax

from ...models import Module, Parameter


def build_module(node: ast.SymbolKind.UninstantiatedDef, line: int) -> Module:  # type: ignore
    """
    Build a module from the passed informations.
    """
    # Fetch the node with a proper name (for IDE autocomplete)
    mod: ast.UninstantiatedDefSymbol = node

    # Extract the connections from the CST
    conns: list[syntax.NamedPortConnectionSyntax] = [
        x for x in mod.syntax.connections if type(x) is syntax.NamedPortConnectionSyntax
    ]

    # Extract the connections
    connections: list[tuple[str, str]] = []
    for conn, name in zip(conns, mod.portNames):
        connections.append((name, str(conn.expr)))

    # Extract the parameters
    params = []
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
            match type(parameter):
                case syntax.NamedParamAssignmentSyntax:
                    name = str(parameter.name)  # type: ignore
                    val = str(parameter.expr) if parameter.expr else ""
                case syntax.OrderedParamAssignmentSyntax:
                    val = str(parameter.expr) if parameter.expr else ""

            params.append(Parameter(name=name, hdl_value=val))

    # Build the Module
    return Module(
        name=node.name,
        entity=mod.definitionName,
        connections=connections,
        params=params,
        line=line,
    )
