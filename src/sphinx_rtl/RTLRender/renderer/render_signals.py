# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the signals section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component, Signal
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_ref,
    render_dropdown,
    render_markdown,
    render_flex_array,
    TreeRenderer,
)
from ..classifier import ElementClassifier


# Class
class SignalRTLRender:
    """
    Define the renderer for the signals block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component signals
        """

        # Do we have anything to render ?
        if len(comp.signals) == 0:
            return

        # Does the config specify us something ?
        if comp.render.signals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Signals", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Signals list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.signals)} element{"s" if len(comp.signals) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # Into the body, let's add a table
        # Configure the table
        headers = [
            "Name",
            "Description",
            "Type",
            "Size",
            "Kind",
        ]
        widths = [1, 3, 1, 2, 2]

        # Build the caches
        clocks: dict[str, nodes.Element] = {}
        resets: dict[str, nodes.Element] = {}

        # Classify the elements
        classifier = ElementClassifier[Signal]()
        tree = classifier.build_tree(comp.signals)

        # Render the elements
        renderer = TreeRenderer[Signal](
            headers=headers,
            width=widths,
            row_renderer=lambda tbl, p: self.parent.utils.draw_port_signal_row(
                tbl, p, comp, clocks, resets, headers
            ),
        )
        renderer.render(tree, body)
