# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the register map section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx.util import logging

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_markdown,
    render_dropdown,
    render_table_header,
    render_table_line,
    render_raw_code,
    render_tabs,
)
from .register_generator import (
    compute_register_layout,
    PYGMENTS_HEADER_LANG,
    HEADER_CALLBACKS,
    HEADER_LANGUAGES,
)

# Configure the logger
logger = logging.getLogger(__name__)


# Class
class RegisterRTLRender:
    """
    Define the renderer for the register map.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component register map, if needed.
        This also generates some examples of C and Rust code ready to be copied from the documentation into the embedded firmware.
        """

        # Is there anything to render
        if len(comp.config.register) == 0:
            return

        # Create our section
        section = self.parent.create_section(
            root, "Register Map", comp.file.name.rsplit(".", 1)[0]
        )

        title = nodes.paragraph()
        title += nodes.Text("Register Map")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.config.register)} register{"s" if len(comp.config.register) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # First, process the register to sort them in order
        registers = sorted(comp.config.register, key=lambda x: x[1])

        # Render a dropdown into it
        dd, body = render_dropdown(title, is_open=True)

        # Add a little bit of text
        table_name = nodes.paragraph(classes=["sd-mt-3"])
        table_name += nodes.strong("", text="List of registers :")
        body += table_name

        # Render the table header
        headers = ["Name", "Offset", "Size", "Description"]
        widths = [2, 1, 1, 3]

        table, table_body = render_table_header(headers, widths=widths)

        # Render the registers
        for register in registers:

            # Build the cells
            cells = [
                nodes.paragraph(),
                nodes.paragraph(),
                nodes.paragraph(),
                nodes.paragraph(),
            ]

            # Add the elements of the table
            cells[0] += nodes.Text(register[0])
            cells[1] += nodes.Text(str(register[1]))
            cells[2] += nodes.Text(str(register[2]))
            cells[3] += render_markdown(
                register[3], comp.file.path, self.parent.base_doc
            )

            # Render the table
            render_table_line(table_body, cells)

        # Add the table to the body
        body += table

        # Define an embedded software structure.
        inst_name = nodes.paragraph(classes=["sd-mt-3"])
        inst_name += nodes.strong("", text="Embedded software structures")
        body += inst_name

        # Build the software layout
        layout = compute_register_layout(registers)

        # Render the templates
        tab_head, tab_elements = render_tabs(HEADER_LANGUAGES, group="Embedded")

        # For each languages, fetch the current rendering
        for lang, tab in tab_elements.items():

            func = HEADER_CALLBACKS.get(lang)
            if func is None:
                tab += nodes.error(
                    f"The provided callbacks was not found for the language {lang}. This is a BUG. Fill and submit a report.",
                )
                continue

            # Now, call the function
            content = func(comp.name, layout)

            # Get the color
            color_lang = PYGMENTS_HEADER_LANG.get(lang)
            if color_lang is None:
                color_lang = "c"
                logger.warning(f"Using default color rendering scheme (c) for {lang}")

            # Add the the formatted code to the tab
            tab += render_raw_code(content, color_lang)

        body += tab_head

        # Add ourselves to the root
        section += dd
