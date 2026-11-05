# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Define private helpers for the class to be used for other.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component, Signal, Port
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_markdown,
    render_table_line,
    render_ref,
)


# Class
class RTLRenderUtils:
    """
    Define the renderer for the assigns block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def get_domain_badge(
        self, name: str, domain_cache: dict[str, nodes.Element]
    ) -> nodes.Element:
        """
        Return the badge for a specific key. Especially useful for clocks and resets.
        """

        # Do we need to create an entry ?
        if name not in domain_cache:
            color = self.parent.DOMAIN_COLORS[
                len(domain_cache) % len(self.parent.DOMAIN_COLORS)
            ]
            domain_cache[name] = render_badge(name, color, outline=True)

        return domain_cache[name]

    def draw_port_signal_row(
        self,
        table: nodes.table,
        element: Port | Signal,
        comp: Component,
        clocks_cache: dict[str, nodes.Element],
        resets_cache: dict[str, nodes.Element],
        headers: list[str] = [],
    ) -> None:
        """
        Insert a line for a port in the table.
        """

        # Fetch the ref_type
        reftype = "signal" if type(element) is Signal else "port"

        # Name
        element_name = nodes.paragraph()
        element_name += render_ref(element.name, comp.name, reftype, self.parent.refs)
        element_name += nodes.Text(element.name.strip())

        # Description
        element_desc = render_markdown(
            element.description, comp.file.path, self.parent.base_doc
        )

        # Type
        element_type = nodes.literal(text=element.hdl_type.strip())

        # Direction
        match element.direction:
            case "input":
                element_dir = render_badge("Input", BadgeColor.GREEN, outline=True)
            case "output":
                element_dir = render_badge("Output", BadgeColor.BLUE, outline=True)
            case _:
                element_dir = render_badge(
                    element.direction, BadgeColor.RED, outline=True
                )

        # Polarity
        if element.hdl_polarity.lower() == "negative":
            element_pol = render_badge("Negative", BadgeColor.RED, outline=True)
        else:
            element_pol = nodes.Text("-")

        # Size
        element_size = nodes.paragraph()
        for begin, end in zip(element.hdl_size[::2], element.hdl_size[1::2]):
            if begin != end:
                element_size += nodes.literal(text=f"[{begin} : {end}]")
                element_size += nodes.inline(" ", " ")

        if len(element_size) == 0:
            element_size = nodes.Text("-")

        # Combinatorial type ?
        if not element.hdl_sync:
            element_kind = render_badge("Combinatorial", BadgeColor.GREEN, outline=True)
        else:
            element_kind = render_badge("Register", BadgeColor.ORANGE, outline=True)

            # Clock domain
            clk_badge = self.get_domain_badge(element.hdl_sync[0], clocks_cache)
            element_kind += nodes.inline(" ", " ")
            element_kind += clk_badge

        # Reset domain
        if element.hdl_reset:
            rst_badge = self.get_domain_badge(element.hdl_reset[0], resets_cache)
            element_kind += nodes.inline(" ", " ")
            element_kind += rst_badge

        # First, build the table content based on what the headers are asking !
        table_content = []
        headers_l = [x.lower() for x in headers]

        if type(element) is Port:

            if "name" in headers_l:
                table_content.append(element_name)
            if "direction" in headers_l:
                table_content.append(element_dir)
            if "description" in headers_l:
                table_content.append(element_desc)
            if "type" in headers_l:
                table_content.append(element_type)
            if "size" in headers_l:
                table_content.append(element_size)
            if "kind" in headers_l:
                table_content.append(element_kind)
            if "polarity" in headers_l:
                table_content.append(element_pol)

        elif type(element) is Signal:

            if "name" in headers_l:
                table_content.append(element_name)
            if "description" in headers_l:
                table_content.append(element_desc)
            if "type" in headers_l:
                table_content.append(element_type)
            if "size" in headers_l:
                table_content.append(element_size)
            if "kind" in headers_l:
                table_content.append(element_kind)

        # Render the table as needed
        render_table_line(
            table,
            table_content,
        )
