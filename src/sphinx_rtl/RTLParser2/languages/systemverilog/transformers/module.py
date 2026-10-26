# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Module transformer
# ----------------------------------------------------------------------------

# Import
import re

from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Module, Parameter
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line, collect
from sphinx_rtl.RTLParser2.languages.systemverilog.queries import (
    MODULE_CASE_Q,
    MODULE_IF_Q,
    MODULE_LOOP_Q,
    MODULE_PARAM_Q,
    MODULE_PORT_Q,
)

# Compile an RE expression to filter assignments
_CMP = re.compile(r"\s*(<=|>=|==|!=|<|>)\s*")


# Get markers where we shall stop
GENERATE_KINDS = {
    "loop_generate_construct": "loop",
    "if_generate_construct": "if",
    "case_generate_construct": "case",
    "generate_region": "region",
}
STOP = {"module_declaration", "interface_declaration", "program_declaration"}


def loop_bound(init: str, cond: str) -> str:
    """'i = 0' + 'i < NUM_LANES' -> 'NUM_LANES'"""
    var = init.split("=")[0].split()[-1]

    m = _CMP.search(cond)
    if not m:
        return cond.strip()
    lhs, rhs = cond[: m.start()].strip(), cond[m.end() :].strip()

    # 'i < N' -> N ; '2 > i' -> 2
    return rhs if lhs == var else lhs


def generate_info(node: Node, source: bytes) -> tuple[bool, bool, str]:
    """-> (is_conditional, is_repeated, condition)"""
    cur = node.parent
    parts = []
    cond = rep = False

    while cur is not None and cur.type not in STOP:
        q = {
            "loop_generate_construct": MODULE_LOOP_Q,
            "if_generate_construct": MODULE_IF_Q,
            "case_generate_construct": MODULE_CASE_Q,
        }.get(cur.type)
        if q:
            for _, caps in QueryCursor(q).matches(cur):
                g = caps["gen"][0]
                if g.id != cur.id:
                    continue
                if cur.type == "loop_generate_construct":
                    rep = True
                    parts.append(
                        loop_bound(
                            get_text(caps["init"][0], source),
                            get_text(caps["cond"][0], source),
                        )
                    )
                else:
                    cond = True
                    parts.append(get_text(caps["cond"][0], source))
        cur = cur.parent

    return cond, rep, " / ".join(reversed(parts))


def VerilogTransformerModule(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Module | None:

    if (
        ("module.node" not in nodes)
        or ("module.instance" not in nodes)
        or ("module.instance.name" not in nodes)
        or ("module.instance.type" not in nodes)
    ):
        return None

    # Allocate output
    module = Module()

    # Main elements
    module.line = get_line(nodes["module.node"][0])
    module.entity = get_text(nodes["module.instance.type"][0], source)

    # This name may contain some sizing
    raw_type = get_text(nodes["module.instance.name"][0], source)
    size = []
    if "[" in raw_type:
        module.name = raw_type.split("[")[0].strip()
        size = [
            x.strip()
            for x in raw_type.split("[")[-1].removesuffix("]").strip().split(":")
        ]
    else:
        module.name = raw_type

    # Define a small lambda function to get the root container for our
    # 2nd layer request
    first = lambda k: nodes[k][0] if k in nodes else None

    # Add the parameters
    for param in collect(MODULE_PARAM_Q, first("module.parameters")):
        parameter = Parameter()
        parameter.line = get_line(param["node"])

        match param["kind"]:
            case "named_parameter_assignment":
                parameter.name = get_text(param["name"], source)
                parameter.hdl_value = get_text(param["value"], source)
            case "ordered_parameter_assignment":
                parameter.hdl_value = get_text(param["value"], source)

        module.params.append(parameter)

    # Add the ports
    for port in collect(MODULE_PORT_Q, first("ports.list")):
        rhs = lhs = ""
        match port["kind"]:
            case "named_port_connection":
                rhs = get_text(port["name"], source)
                lhs = get_text(port["value"], source)
            case "ordered_port_connection":
                lhs = get_text(port["value"], source)
        module.connections.append((rhs, lhs))

    # Are we within a generate in some kind ?
    cond, rep, text = generate_info(nodes["module.node"][0], source)

    module.isConditionnal = cond
    module.isRepeated = rep

    if cond:
        module.condition = text
    elif rep:
        module.count = text

    # Finally, handle some weird style declaration :
    if len(size) > 0:

        buf = []
        for s in size:

            # If a number, cast and append to the buffer
            if s.isdigit():
                count = s
                buf.append(count)

            # If a text, let's suppose it's User provided and exit the loop.
            else:
                module.count = s
                break

        # Append the max
        module.count = max(buf)
        module.isRepeated = True

    return module
