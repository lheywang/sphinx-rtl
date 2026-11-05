# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the modports section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component, Port
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    render_markdown,
    TreeRenderer,
)
from sphinx_rtl.RTLRender.classifier import ElementClassifier


# Class
class ModportRTLRender:
    """
    Define the renderer for the enums block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component interfaces.
        """

        # Do we have anything to render ?
        if len(comp.modports) == 0:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Modports", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Modport list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.modports)} element{"s" if len(comp.modports) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # Allocate memory and render the assignments.
        for modport in comp.modports:

            # Build the title for the modport
            modport_title = nodes.paragraph()
            modport_title += nodes.Text(modport.name)

            # Create a sub dd for the current dropdown
            modport_dd, modport_body = render_dropdown(modport_title)

            # Let's add the description to it
            modport_description = nodes.paragraph()
            modport_description += render_markdown(
                modport.description, comp.file.path, self.parent.base_doc
            )
            modport_body += modport_description

            # Now add the different elements into an array
            # Into the body, let's add a table
            # Configure the table
            headers = ["Name", "Direction", "Description", "Type", "Size"]
            widths = [1, 3, 3, 1, 2, 2, 1]

            # Build the caches
            clocks: dict[str, nodes.Element] = {}
            resets: dict[str, nodes.Element] = {}

            # Classify the elements
            classifier = ElementClassifier[Port]()
            tree = classifier.build_tree(modport.signals)

            # Render the elements
            renderer = TreeRenderer[Port](
                headers=headers,
                width=widths,
                row_renderer=lambda tbl, p: self.parent.utils.draw_port_signal_row(
                    tbl, p, comp, clocks, resets, headers
                ),
            )
            renderer.render(tree, modport_body)

            # Add ourselves to the main body
            body += modport_dd
