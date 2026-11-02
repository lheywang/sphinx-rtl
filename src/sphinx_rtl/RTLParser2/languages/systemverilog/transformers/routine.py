# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Routine transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Function, Port
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from sphinx_rtl.RTLParser2.languages.systemverilog.queries import (
    FUNCTIONS_PARTS_Q,
    FUNCTIONS_PORTS_Q,
)

from .utils import get_size_and_type


# Functions
def VerilogTransformerRoutine(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Function | None:

    node = nodes["function.node"][0]

    cur = node.parent
    while cur is not None:
        if cur.type == "class_declaration":
            return None
        if cur.type in (
            "module_declaration",
            "interface_declaration",
            "package_declaration",
        ):
            break
        cur = cur.parent

    body = nodes["function.body"][0]
    parts = next(
        (
            c
            for _, c in QueryCursor(FUNCTIONS_PARTS_Q).matches(body)
            if c["body"][0].id == body.id
        ),
        None,
    )
    if parts is None:
        return None

    # Fetch all the args
    args = []
    if "ports" in parts:
        for _, c in QueryCursor(FUNCTIONS_PORTS_Q).matches(parts["ports"][0]):

            typ, siz = get_size_and_type(
                get_text(c["type"][0], source) if "type" in c else ""
            )

            args.append(
                {
                    "direction": (
                        get_text(c["dir"][0], source) if "dir" in c else "input"
                    ),
                    "type": typ,
                    "size": siz,
                    "name": get_text(c["name"][0], source),
                    "default": (
                        get_text(c["default"][0], source) if "default" in c else ""
                    ),
                }
            )

    # Format the output and inputs correctly
    out = Port(name=get_text(parts["ret"][0], source) if "ret" in parts else "void")
    args_f = [
        Port(
            name=c["name"],
            hdl_type=c["type"],
            hdl_size=c["size"],
            direction=c["direction"],
        )
        for c in args
    ]

    # Build the output object
    func = Function()
    func.line = get_line(node)
    func.name = get_text(parts["name"][0], source)
    func.func_inputs = args_f
    func.func_outputs = [out]

    return func
