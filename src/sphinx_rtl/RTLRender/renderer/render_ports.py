# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the ports section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component, Port
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    TreeRenderer,
)
from sphinx_rtl.RTLRender.classifier import ElementClassifier


# Class
class PortRTLRender:
    """
    Define the renderer for the ports block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component ports as grouped by the system
        """

        # Do we have anything to render ?
        if len(comp.ports) == 0:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Ports", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Ports list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.ports)} element{"s" if len(comp.ports) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # Configure the table
        headers = [
            "Name",
            "Direction",
            "Description",
            "Type",
            "Size",
            "Kind",
            "Polarity",
        ]
        widths = [1, 3, 3, 1, 2, 2, 1]

        # Initialize some cache for the badges
        clocks: dict[str, nodes.Element] = {}
        resets: dict[str, nodes.Element] = {}

        # Classify the elements
        classifier = ElementClassifier[Port]()
        tree = classifier.build_tree(comp.ports)

        # Render the element
        renderer = TreeRenderer[Port](
            headers=headers,
            width=widths,
            row_renderer=lambda tbl, p: self.parent.utils.draw_port_signal_row(
                tbl, p, comp, clocks, resets, headers
            ),
        )
        renderer.render(tree, body)
