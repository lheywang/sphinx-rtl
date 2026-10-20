# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Parameter transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Enum, Structure
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VHDLTransformerType(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Enum | Structure | None:

    # Is there anything for us ?
    if "type.name" not in nodes or "type.array" not in nodes:
        return None

    line = get_line(nodes["type.name"][0])
    name = get_text(nodes["type.name"][0], source)

    ret = None
    if "type.array" in nodes and nodes["type.array"]:
        definition = get_text(nodes["type.array"][0], source)
        ret = Enum(name=name, line=line, members=[definition])

    if "type.enum" in nodes and nodes["type.enum"]:
        enum_nodes = nodes["type.enum"]
        members = [get_text(n, source) for n in enum_nodes]
        ret = Enum(name=name, description="", line=line, members=members)

    if "type.record" in nodes and nodes["type.record"]:
        ret = Structure(
            name=name, description="", line=line, signals=[], isPacked=False
        )

    if "type.definition" in nodes and nodes["type.definition"]:
        definition = get_text(nodes["type.definition"][0], source)
        ret = Enum(name=name, description="", line=line, members=[definition])

    print("TO-REWORK", ret)
    return ret
