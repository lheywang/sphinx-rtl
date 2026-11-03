# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Modport transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Modport, Port
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from sphinx_rtl.RTLParser2.languages.systemverilog.queries import MODPORTS_PORTS_Q


# Functions
def VerilogTransformerModport(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Modport | None:

    if "modport.node" not in nodes or "modport.name" not in nodes:
        return None
    item = nodes["modport.node"][0]

    m = Modport()
    m.name = get_text(nodes["modport.name"][0], source)
    m.line = get_line(item)

    for _, c in QueryCursor(MODPORTS_PORTS_Q).matches(item):
        p = Port()
        p.name = get_text(c["name"][0], source)
        p.direction = get_text(c["dir"][0], source)
        p.line = get_line(c["port"][0])
        m.signals.append(p)

    return m
