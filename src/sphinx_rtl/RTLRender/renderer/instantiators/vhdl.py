# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    03/11/2026
#
# Brief :   Build a VHDL instance example.
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import Component


def instantiate_vhdl(comp: Component) -> str:
    """
    Return a instantiation of a component in VHDL.
    """
    lines: list[str] = []

    # Add the instance name
    lines.append(f"<name>: entity work.{comp.name}\n")

    # Add the parameters
    if len(comp.parameters) > 0:

        # Get the longest name. This enable an alignment to be cleaner.
        longest = max([len(p.name) for p in comp.parameters])

        lines.append("    generic map (\n")

        for index, parameter in enumerate(comp.parameters):
            comma = "" if index == len(comp.parameters) - 1 else ","
            lines.append(
                f"        {parameter.name.ljust(longest)}  => {parameter.hdl_value if parameter.hdl_value else "UNDEFINED"}{comma}\n"
            )

        lines.append("    )\n")

    # Add the ports
    if len(comp.ports) > 0:

        longest = max([len(p.name) for p in comp.ports])

        lines.append("   port map (\n")

        for index, port in enumerate(comp.ports):
            comma = "" if index == len(comp.ports) - 1 else ","
            lines.append(
                f"        {port.name.ljust(longest)}  => i_{port.name}{comma}\n"
            )

        lines.append("    );\n\n")

    # Return the component.
    return "".join(lines)
