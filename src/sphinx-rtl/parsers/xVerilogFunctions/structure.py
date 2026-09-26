# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Build a structure for the module
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast
import pyslang.syntax as syntax
from pyslang import SourceManager

from ...models import Structure, Signal
from .utils import get_size_and_type


def build_struct(node: ast.TypeAliasType, line: int, sm: SourceManager) -> Structure:
    """
    Build the structure object from a passed signal node.

    Another slightly different usage of the standard procedure matching,
    """

    members: list[syntax.StructUnionMemberSyntax] = node.syntax.type.members
    signals: list[Signal] = []
    for member in members:

        # Init variables
        hdl_type: str = ""
        hdl_size: list[str] = []

        # Fetch the raw type
        hdl_type, hdl_size = get_size_and_type(str(member.type))

        # Append the declarators
        hdl_name = ""
        hdl_line = 0

        declarators: list[syntax.DeclaratorSyntax] = member.declarators
        for declarator in declarators:
            hdl_name = str(declarator.name).strip()

            hdl_line = sm.getLineNumber(declarator.sourceRange.start)
            if hdl_line == 0:
                hdl_line = -1

            for dimension in declarator.dimensions:
                _, size = get_size_and_type(str(dimension).strip())
                if size[0] != size[1]:
                    hdl_size.extend(size)

        signals.append(
            Signal(hdl_type=hdl_type, hdl_size=hdl_size, name=hdl_name, line=hdl_line)
        )

    # Build the struct and return it
    return Structure(
        name=node.name.strip(),
        line=line,
        isPacked=not node.isUnpackedStruct,
        signals=signals,
    )
