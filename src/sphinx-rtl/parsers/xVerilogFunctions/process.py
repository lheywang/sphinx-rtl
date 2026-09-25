# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import re
import pyslang.ast as ast
import pyslang.syntax as syntax

from ...models import Process


def build_process(node: ast.ProceduralBlockSymbol, line: int) -> Process:
    """
    Build a process object from the passed source.
    """

    # Get the name (generally empty)
    name = node.name

    # Init variables
    clocks: list[str] = []
    resets: list[str] = []
    targets: list[str] = []

    # Fetch the syntax
    node_syntax: syntax.ProceduralBlockSyntax = node.syntax
    statements: syntax.TimingControlStatementSyntax = node_syntax.statement  # type: ignore

    # Fetch the type. We let it to None for cases
    hdl_type = None
    if (
        node.procedureKind == ast.ProceduralBlockKind.AlwaysFF
        or node.procedureKind == ast.ProceduralBlockKind.AlwaysLatch
    ):
        hdl_type = "flipflop"
    elif node.procedureKind == ast.ProceduralBlockKind.AlwaysComb:
        hdl_type = "comb"

    for statement in str(statements).split("\n"):
        assignements = statement.split("=")

        if len(assignements) > 1:
            lhs = assignements[0].strip()

            # That's a non blocking assignment !
            if "<" in lhs and lhs.split(" ")[0] not in targets:
                targets.append(lhs.split(" ")[0])

    # First, fetch the procedural type:
    if hdl_type is None:
        if "posedge" in statements or "negedge" in statements:
            hdl_type = "flipflop"

    # Now, look for the clocks and resets :
    if hdl_type == "flipflop":

        # Fetch any markers within the passed tokens :
        markers = re.findall(r"(?:posedge|negedge)\s+([a-zA-Z_0-9]+)", str(statements))

        # Identify clock and resets :
        for marker in markers:
            if any(kw in marker.lower() for kw in ("rst", "reset")):
                resets.append(marker)
            else:
                clocks.append(marker)

    # Fetch all the signals names
    signals = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_$]*\b", str(statements)))
    exclude = set(clocks) | set(resets)
    signals = signals - exclude

    # Build the output port
    return Process(
        name=name,
        hdl_type=str(hdl_type),
        hdl_clock=clocks,
        hdl_reset=resets,
        signals_write=targets,
        signals=list(signals),
        line=line,
    )
