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
from pyslang import SourceManager

from ...models import Module, Parameter


def get_module_from_instantiation(
    members: list[syntax.HierarchyInstantiationSyntax],
    sm: SourceManager,
) -> list[Module]:
    """
    Fetch the different elements and build a Module from the raw Hierarchy.
    """

    modules: list[Module] = []
    for member in members:

        mod_entity = str(member.type).strip()
        temp_line = sm.getLineNumber(member.sourceRange.start)
        mod_line = -1
        if temp_line != 0:
            mod_line = temp_line

        instances: list[syntax.HierarchicalInstanceSyntax] = member.instances
        for inst in instances:
            mod_name = str(inst.decl.name).strip()

            conns: list[
                syntax.NamedPortConnectionSyntax | syntax.OrderedPortConnectionSyntax
            ] = [
                x
                for x in inst.connections
                if type(x) is syntax.NamedPortConnectionSyntax
                or type(x) is syntax.OrderedPortConnectionSyntax
            ]

            # Parse the connection syntax.
            # As we don't have the portConnections, we need to do it by hand.
            connections: list[tuple[str, str]] = []
            for conn in conns:

                expr = str(conn).strip()

                if "." in expr:

                    # Split around the parentheses that are mandatory
                    expr_elements = [
                        x.strip() for x in expr.replace(")", "").split("(")
                    ]
                    port = expr_elements[0].removeprefix(".")
                    signal = expr_connection = re.sub(
                        "\\[.*\\]", "", expr_elements[-1]
                    ).strip()
                    connections.append((port, signal))
                else:
                    # Is there some slicing in there ? As we don't want them, let's remove them.
                    expr_connection = re.sub("\\[.*\\]", "", expr).strip()
                    connections.append(("", expr_connection))

            # Finally fetch the parameters
            parameters: list[
                syntax.NamedParamAssignmentSyntax | syntax.OrderedParamAssignmentSyntax
            ] = (
                [
                    x
                    for x in member.parameters
                    if type(x) == syntax.NamedParamAssignmentSyntax
                    or type(x) == syntax.OrderedParamAssignmentSyntax
                ]
                if member.parameters is not None
                else []
            )

            params: list[Parameter] = []
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

                param_line = sm.getLineNumber(parameter.sourceRange.start)
                if param_line == 0:
                    param_line = -1

                params.append(Parameter(name=name, hdl_value=val, line=param_line))

            # Add the module
            modules.append(
                Module(
                    name=mod_name,
                    entity=mod_entity,
                    line=mod_line,
                    connections=connections,
                    params=params,
                )
            )

    return modules


def build_generate(
    node: ast.GenerateBlockSymbol | ast.GenerateBlockArraySymbol,
    line: int,
    sm: SourceManager,
) -> list[Module]:
    """
    Build the signal object from a passed signal node.

    Another slightly different usage of the standard procedure matching,
    """

    # Allocate memory
    modules: list[Module] = []

    # -----------------------------------------------------------------------------
    # CONDITIONAL GENERATE BLOCK
    # -----------------------------------------------------------------------------
    if node.kind == ast.SymbolKind.GenerateBlock:
        cond: ast.GenerateBlockSymbol = node  # type: ignore

        # Extract the condition :
        cond_identifier: str = str(cond.conditionExpression.syntax.identifier)

        # Extract the members :
        members: list[syntax.HierarchyInstantiationSyntax] = cond.syntax.members
        temp_modules = get_module_from_instantiation(members, sm)

        # Add the global infos :
        for module in temp_modules:
            module.condition = cond_identifier
            module.isConditionnal = True
            modules.append(module)

    # -----------------------------------------------------------------------------
    # LOOP GENERATE BLOCK
    # -----------------------------------------------------------------------------
    elif node.kind == ast.SymbolKind.GenerateBlockArray:
        loop: ast.GenerateBlockArraySymbol = node  # type: ignore
        entries: list[ast.GenerateBlockSymbol] = loop.entries

        if len(entries) == 0:
            count = re.split("[=<>]", str(loop.stopExpression.syntax).strip())[
                -1
            ].strip()
            if count.isdigit():
                repeat = True if int(count) > 1 else False
            else:
                repeat = True

        else:
            count = f"{len(entries)}"
            repeat = True if len(entries) > 1 else False

        mod_entity = ""
        mod_name = ""
        mod_line = -1

        # Extract the data
        members: list[syntax.HierarchyInstantiationSyntax] = loop.syntax.block.members
        temp_modules = get_module_from_instantiation(members, sm)

        # Add the global infos :
        for module in temp_modules:
            module.count = count
            module.isRepeated = repeat
            modules.append(module)

    # Return the raw list
    return modules
