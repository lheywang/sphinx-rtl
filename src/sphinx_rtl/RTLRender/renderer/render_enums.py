# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the enums section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_ref,
    render_dropdown,
    render_markdown,
    render_flex_array,
)


# Class
class EnumRTLRender:
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
        Render the component enums
        """

        # Do we have anything to render ?
        if len(comp.enums) == 0:
            return

        # Does the config specify us something ?
        if comp.render.internals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Enums", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Enum list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.enums)} element{"s" if len(comp.enums) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # For each enums, let's add another dropdown in here
        for enum in comp.enums:

            # Build the dropdown
            enum_title = nodes.paragraph()
            enum_title += render_ref(enum.name, comp.name, "enum", self.parent.refs)
            enum_title += nodes.Text(enum.name)
            enum_title += nodes.inline(" ", " ")
            enum_title += render_badge(
                f"{len(enum.values)} values", BadgeColor.CYAN, outline=True
            )

            enum_dd, enum_body = render_dropdown(enum_title, is_open=True)
            body += enum_dd

            # Add the elements to it
            enum_description = nodes.paragraph()
            if enum.description:
                enum_description += render_markdown(
                    enum.description, comp.file.path, self.parent.base_doc
                )

            enum_body += enum_description

            # Add the elements into it, as a list
            elements = []
            for member, value in zip(enum.members, enum.values):

                row = []
                value_name = nodes.paragraph()
                value_name += nodes.inline(text="• ")
                value_name += render_ref(
                    member, comp.name, "enum-value", self.parent.refs
                )
                value_name += nodes.strong(text=member)
                row.append(value_name)

                value_def = nodes.paragraph()
                value_def += render_badge(
                    f"Value : {value}", BadgeColor.GREEN, outline=True
                )
                row.append(value_def)

                elements.append(row)

            # Render the list
            enum_body += render_flex_array(elements)
