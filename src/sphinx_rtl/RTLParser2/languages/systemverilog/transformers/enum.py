# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Enum transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Enum, Structure, Signal
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line
from sphinx_rtl.RTLParser2.languages.systemverilog.queries import ENUM_Q_MEMBERS

from .utils import get_size_and_type


# Functions
def VerilogTransformerEnum(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Enum | Structure | None:

    # Is there everything we need ?
    if ("typedef.node" not in nodes) or ("typedef.name" not in nodes):
        return None

    isEnum = True
    internals: list[Signal | tuple[str, str]] = []
    for index, capture in QueryCursor(ENUM_Q_MEMBERS).matches(nodes["typedef.node"][0]):

        match index:

            # We matched something within a struct. Use that.
            case 0:
                isEnum = False
                signal = Signal()

                signal.line = get_line(capture["member.type"][0])
                signal.name = get_text(capture["member.name"][0], source)
                signal.hdl_type, signal.hdl_size = get_size_and_type(
                    get_text(capture["member.type"][0], source)
                )
                signal.hdl_value = (
                    get_text(capture["member.value"][0], source)
                    if "member.value" in capture
                    else ""
                )

                internals.append(signal)

            # We matched an enum. Using it.
            case 1:
                item_name = get_text(capture["enum.item"][0], source)
                item_value = (
                    get_text(capture["enum.value"][0], source)
                    if "enum.value" in capture
                    else ""
                )
                internals.append((item_name, item_value))

    if isEnum:
        item = Enum()

        for item_name, item_value in internals:
            item.members.append(item_name)
            item.values.append(item_value)
    else:
        item = Structure()

        item.signals = internals  # type: ignore

    item.line = get_line(nodes["typedef.node"][0])
    item.name = get_text(nodes["typedef.name"][0], source)

    return None
