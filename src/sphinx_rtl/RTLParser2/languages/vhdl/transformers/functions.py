# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Function transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Function, Port
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from .utils import get_size_type


# Functions
def VHDLTransformerFunction(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Function | None:

    if (
        ("func.node" not in nodes)
        or ("func.args" not in nodes)
        or ("func.name" not in nodes)
        or ("func.return" not in nodes)
    ):
        return None

    function = Function()
    function.name = get_text(nodes["func.name"][0], source)
    function.line = get_line(nodes["func.node"][0])

    # Build the inputs
    args_text = get_text(nodes["func.args"][0].named_children[0], source)
    args_line = get_line(nodes["func.args"][0].named_children[0])

    for arg_text in args_text.split(";"):

        # Split on the names
        names, subtype = arg_text.split(":")

        # Get size and type
        typ, size = get_size_type(subtype)

        # Get all names
        for name in names.split(","):

            name = name.strip()

            function.func_inputs.append(
                Port(name=name, line=args_line, hdl_type=typ, hdl_size=size)
            )

    # Build the output type
    function.func_outputs.append(
        Port(
            hdl_type=get_text(nodes["func.return"][0], source),
            line=get_line(nodes["func.return"][0]),
        )
    )

    return function
