# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Assign transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Assignment
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line


# Functions
def VHDLTransformerAssign(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Assignment:

    # Is there anything for us ?
    if "assign.concurrent" in nodes and nodes["assign.concurrent"]:
        line = get_line(nodes["assign.concurrent"][0])
        wvf = get_text(nodes["assign.waveform"][0], source)
        target = get_text(nodes["assign.target"][0], source)

        # We don't know, the IR will do it's job then !
        return Assignment(line=line, target=target, source=[wvf])

    if "assign.conditional" in nodes and nodes["assign.conditional"]:
        line = get_line(nodes["assign.conditional"][0])
        wvf = get_text(nodes["assign.waveform"][0], source)
        target = get_text(nodes["assign.target"][0], source)

        # An condition is mandatory as a mux.
        return Assignment(line=line, target=target, source=[wvf], isComb=True)

    return Assignment()
