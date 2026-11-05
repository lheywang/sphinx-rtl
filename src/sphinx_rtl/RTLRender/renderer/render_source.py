# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the source code of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    render_code,
)


# Class
class SourceRTLRender:
    """
    Define the renderer for the source code block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component source on the page, if needed.
        This function may do nothing as specified within the component configuration flags.
        """

        # Do we have things to render ?
        if comp.render.showSource == False:
            return

        # Create our section
        section = self.parent.create_section(
            root, "Source", comp.file.name.rsplit(".", 1)[0]
        )

        # Create the title
        title = nodes.paragraph()
        title += nodes.Text("Raw source")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            "Full file",
            BadgeColor.CYAN,
            outline=True,
        )

        # Build a dropdown (default to hidden).
        # This let the page small enough to be read by humans.
        dd, body = render_dropdown(title, is_open=False)

        # Now, let's add the code
        body += render_code(comp.file.path, comp.lang)

        # Add ourselves to the root
        section += dd
