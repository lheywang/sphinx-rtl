# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/10/2026
#
# Brief :   Define the Process transformer
# ----------------------------------------------------------------------------

# Import
import re

from tree_sitter import Node, QueryCursor

from sphinx_rtl.models import Process
from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from sphinx_rtl.RTLParser2.languages.systemverilog.queries import (
    PROCESS_EVENT_CTRL_Q,
    PROCESS_EVENT_LEAF_Q,
    PROCESS_EVENT_WRITE_Q,
)

# Define the simple regex to sort numeric constants
_IDENT = re.compile(r"[A-Za-z_]\w*|\\\S+")


# Functions
def VerilogTransformerProcess(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Process | None:

    # Fetch the root node
    node = nodes["process.node"][0]
    kind = (
        get_text(nodes["process.kind"][0], source)
        if "process.kind" in nodes
        else node.type.removesuffix("_construct")
    )

    # Extract the kind, the sensitivity and signals.
    sensitivity = ""
    signals: list[dict[str, str]] = []
    for _, c in QueryCursor(PROCESS_EVENT_CTRL_Q).matches(node):
        ec = c["ec"][0]
        if source[nodes["process.kind"][0].end_byte : ec.start_byte].strip():
            continue
        sensitivity = get_text(ec, source)
        for _, l in QueryCursor(PROCESS_EVENT_LEAF_Q).matches(ec):
            signals.append(
                {
                    "edge": get_text(l["edge"][0], source) if "edge" in l else "",
                    "signal": get_text(l["signal"][0], source),
                }
            )

    # Fetch written signals
    written = sorted(
        {
            get_text(c["lhs"][0], source)
            for _, c in QueryCursor(PROCESS_EVENT_WRITE_Q).matches(node)
        }
    )

    # Fetch the rode signals and filter the constants.
    reads = sorted(
        {
            get_text(c["leaf"][0], source) if "leaf" in c else ""
            for _, c in QueryCursor(PROCESS_EVENT_WRITE_Q).matches(node)
        }
    )
    reads = sorted({t for t in reads if _IDENT.match(t)})

    # Build the output
    proc = Process()
    proc.line = get_line(node)

    if len(sensitivity) > 0:
        for signal in signals:
            name = signal["signal"]

            if "clk" in name or "clock" in name:
                proc.hdl_clock.append(name)
            elif "rst" in name or "reset" in name:
                proc.hdl_reset.append(name)

    # Add the process IOs
    proc.signals = reads
    proc.signals_write = written

    # Match the process type
    proc_type = {
        "always_ff": "flipflop",
        "always_latch": "flipflop",
        "always_comb": "combinatorial",
        "always": "combinatorial" if len(proc.hdl_clock) == 0 else "flipflop",
        "initial": "combinatorial",
        "final": "combinatorial",
    }

    proc.hdl_type = proc_type[kind]

    return proc
