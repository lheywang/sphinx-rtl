# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Process transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Process
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line, get_identifiers

from .utils import VHDL_KEYWORDS_AND_TYPES


# Helpers
def extract_process_signals(
    process_body_node: Node, source: bytes
) -> tuple[list[str], list[str]]:
    """
    Extract IO signals from the body of the process
    """
    signals_write = []
    all_read_signals = []

    def traverse(n: Node, is_target: bool = False):
        if n.type == "identifier":
            name = get_text(n, source)

            if name.lower() not in VHDL_KEYWORDS_AND_TYPES:
                if is_target:
                    if name not in signals_write:
                        signals_write.append(name)
                else:
                    if name not in all_read_signals:
                        all_read_signals.append(name)
            return

        if n.type in {
            "simple_waveform_assignment",
            "conditional_signal_assignment",
            "simple_variable_assignment",
        }:
            for child in n.children:
                if child.type in {"_target", "name", "aggregate"}:
                    traverse(child, is_target=True)
                else:
                    traverse(child, is_target=False)
            return

        for child in n.children:
            traverse(child, is_target)

    traverse(process_body_node)

    signals_read = [s for s in all_read_signals if s not in signals_write]

    return signals_write, signals_read


# Functions
def VHDLTransformerProcess(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Process | None:

    # Is there anything for us ?
    if "process.node" not in nodes:
        return None

    line = get_line(nodes["process.node"][0])

    name = ""
    if "process.label" in nodes and nodes["process.label"]:
        name = get_text(nodes["process.label"][0], source)

    signals = []
    if "process.sensitivity" in nodes and nodes["process.sensitivity"]:
        sens_node = nodes["process.sensitivity"][0]
        signals = get_identifiers(sens_node, source)

    iow = ior = []
    if "process.body" in nodes and nodes["process.body"]:
        body_node = nodes["process.body"][0]
        iow, ior = extract_process_signals(body_node, source)

    # Now, let's do some maths and set theory here and here
    clocks = [s for s in signals if any(kw in s.lower() for kw in ("clk", "clock"))]
    resets = [s for s in signals if any(kw in s.lower() for kw in ("rst", "reset"))]

    # Merge the ior signals
    filtered_ior = list((set(ior) | set(iow)) - (set(clocks) | set(resets)))

    # Build the output object
    return Process(
        line=line,
        name=name,
        signals_write=iow,
        signals=filtered_ior,
        hdl_clock=clocks,
        hdl_reset=resets,
    )
