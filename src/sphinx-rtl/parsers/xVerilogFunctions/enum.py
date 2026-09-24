# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast

from ...models import Enum


def build_enum(node: ast.TypeAliasType, line: int) -> Enum:
    """
    Build the enum definition from a TypeAlias node.
    """
    # Fetch the resolved type
    node_type: str = str(node.targetType.type)
    width = node.bitstreamWidth

    # Extract the elements
    enum, name = node_type.split("}", 1) if "}" in node_type else ("", "")

    # Allocate variables
    values: list[int] = []
    ids: list[str] = []

    # Extract the elements :
    if enum.startswith("enum{"):
        members = enum.split("enum{", 1)[1].split(",")

        # Extract the values
        for member in members:
            temp = member.split("=")

            if len(temp) > 1:
                ids.append(temp[0])
                values.append(int(temp[1].replace(f"{width}'d", "")))

    # Build the output
    return Enum(name=name.split(".")[-1], values=values, members=ids, line=line)
