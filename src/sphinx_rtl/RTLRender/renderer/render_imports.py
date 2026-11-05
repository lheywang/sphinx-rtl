# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the import section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_ref,
    render_dropdown,
    render_bullet_list,
)


# Class
class ImportRTLRender:
    """
    Define the renderer for the imports block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component imports
        """
        # Do we have anything to render ?
        if len(comp.imports) == 0:
            return

        # Does the config specify us something ?
        if comp.render.internals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Imports", comp.file.name.rsplit(".", 1)[0]
        )

        # For each import, render it under the form of the source library and a list of nodes.
        elements = []
        count = 0
        for imported in comp.imports:

            line = nodes.paragraph()
            line += render_ref(imported.library, comp.name, "import", self.parent.refs)
            name = nodes.strong()
            name += nodes.Text(imported.library)
            line += name
            line += nodes.inline(" ", " ")

            for element in imported.element:
                if element == "*":
                    line += render_badge(element, BadgeColor.ORANGE)
                else:
                    line += render_badge(element, BadgeColor.GREEN)
                line += nodes.inline(" ", " ")
                count += 1

            elements.append(line)

        # Render the dropdown menu
        # We do that after to ensure we can count the different imports.
        title = nodes.paragraph()
        title += nodes.Text("Imports")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{count} element{"s" if count > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        dd, body = render_dropdown(title, is_open=True)

        # Render the list
        body += render_bullet_list(elements)

        # Add the list to the section
        section += dd
