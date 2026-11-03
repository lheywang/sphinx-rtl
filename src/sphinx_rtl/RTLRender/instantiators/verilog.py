# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    03/11/2026
#
# Brief :   Build a verilog instance example.
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import Component


def instantiate_verilog(comp: Component) -> str:
    """
    Return a instantiation of a component in Verilog.
    """

    lines: list[str] = []

    # Add the entity name
    lines.append(f"{comp.name} <name> ")

    if len(comp.parameters) > 0:
        lines.append("#(\n")

        # Get the longest name. This enable an alignment to be cleaner.
        longest = max([len(p.name) for p in comp.parameters])

        for index, parameter in enumerate(comp.parameters):
            comma = "" if index == len(comp.parameters) - 1 else ","
            lines.append(
                f"    .{parameter.name.ljust(longest)} ({parameter.hdl_value if parameter.hdl_value else "UNDEFINED"}){comma}\n"
            )

        lines.append("\n)(\n")
    else:
        lines.append("(\n")

    # Add the ports
    if len(comp.ports) > 0:

        # Get the longest name. This enable an alignment to be cleaner.
        longest = max([len(p.name) for p in comp.ports])

        for index, port in enumerate(comp.ports):
            comma = "" if index == len(comp.ports) - 1 else ","
            lines.append(f"    .{port.name.ljust(longest)} (i_{port.name}){comma}\n")

    # Add the closure
    lines.append(");\n")

    # Return
    return "".join(lines)
