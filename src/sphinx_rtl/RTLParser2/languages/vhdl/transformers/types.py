# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Parameter transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Enum, Structure, Signal
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from .utils import get_size_type


# Functions
def VHDLTransformerType(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Enum | Structure | None:

    # Is there anything for us ?
    if "type.name" not in nodes:
        return None

    line = get_line(nodes["type.name"][0])
    name = get_text(nodes["type.name"][0], source)

    ret = None
    if "type.array" in nodes and nodes["type.array"]:
        typ, definition = get_size_type(get_text(nodes["type.array"][0], source))
        ret = Enum(name=name, line=line, members=definition, hdl_type=typ)

    elif "type.enum" in nodes and nodes["type.enum"]:

        # Fetch the elements
        enum_nodes = nodes["type.enum"]
        raw_enum = get_text(enum_nodes[0], source).replace("(", "").replace(")", "")

        # Fetch the members
        members = [x.strip() for x in raw_enum.split(",")]
        ret = Enum(name=name, description="", line=line, members=members)

    elif "type.record" in nodes and nodes["type.record"]:
        signals: list[Signal] = []
        for field in nodes["type.fields"]:

            # Get text and line
            field_text = get_text(field, source)
            field_line = get_line(field)

            # Fetch the name and subtype indications
            field_name, subtype = field_text.split(":", 1)
            field_name = field_name.strip()

            typ, size = get_size_type(subtype)

            # Build a signal from it
            signals.append(
                Signal(name=field_name, line=field_line, hdl_type=typ, hdl_size=size)
            )

        ret = Structure(
            name=name, description="", line=line, signals=signals, isPacked=False
        )

    return ret
