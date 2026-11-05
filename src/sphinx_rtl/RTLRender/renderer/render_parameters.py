# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the parameters section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_markdown,
    render_dropdown,
    render_ref,
    render_def_list,
)


# Class
class ParameterRTLRender:
    """
    Define the renderer for the parameters block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render a component parameters.
        """

        # Do we have anything to render ?
        if len(comp.parameters) == 0:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Parameters", comp.file.name.rsplit(".", 1)[0]
        )

        # Build a dropdown menu for ourselves
        title = nodes.paragraph()
        title += nodes.Text("Parameters")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.parameters)} element{"s" if len(comp.parameters) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        dd, body = render_dropdown(title, is_open=True)

        # Allocate the lists
        elements = []
        definitions = []
        for parameter in comp.parameters:

            # Build the logical element
            element = nodes.term()
            element += render_ref(
                parameter.name, comp.name, "parameter", self.parent.refs
            )
            element += nodes.inline(text="• ", classes=["sd-text-muted"])
            name = nodes.strong()
            name += nodes.Text(parameter.name)
            element += name
            element += nodes.inline(" ", " ")
            element += render_badge(
                f"Type : {parameter.hdl_type}", BadgeColor.CYAN, outline=True
            )

            if parameter.hdl_value:
                element += nodes.inline(" ", " ")
                element += render_badge(
                    f"Default : {parameter.hdl_value}", BadgeColor.GREEN, outline=True
                )

            # Add the definition
            definition = nodes.paragraph()
            if parameter.description:
                definition += render_markdown(
                    parameter.description, comp.file.path, self.parent.base_doc
                )
            else:
                definition += nodes.Text("-")

            # Append the elements to the lists
            elements.append(element)
            definitions.append(definition)

        # Render the list
        body += render_def_list(elements, definitions)

        # Add the dropdown to the section
        section += dd
