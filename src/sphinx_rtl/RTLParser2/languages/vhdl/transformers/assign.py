# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Assign transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node, Query, QueryCursor, Language
from tree_sitter_vhdl import language

from sphinx_rtl.models import Assignment
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

VHDL = Language(language())

# Build a custom query for the signals
ID_Q = Query(VHDL, "(identifier) @id")


# Functions
def VHDLTransformerAssign(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Assignment:

    # Is there anything for us ?
    if "assign.concurrent" in nodes and nodes["assign.concurrent"]:
        line = get_line(nodes["assign.concurrent"][0])
        reads = sorted(
            {
                get_text(c["id"][0], source).lower()
                for _, c in QueryCursor(ID_Q).matches(nodes["assign.waveform"][0])
            }
        )
        target = get_text(nodes["assign.target"][0], source)

        # We don't know, the IR will do it's job then !
        return Assignment(line=line, target=target, source=reads)

    if "assign.conditional" in nodes and nodes["assign.conditional"]:
        line = get_line(nodes["assign.conditional"][0])
        reads = sorted(
            {
                get_text(c["id"][0], source).lower()
                for _, c in QueryCursor(ID_Q).matches(nodes["assign.waveform"][0])
            }
        )
        target = get_text(nodes["assign.target"][0], source)

        # An condition is mandatory as a mux.
        return Assignment(line=line, target=target, source=reads, isComb=True)

    return Assignment()
