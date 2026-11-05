# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the functions section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    render_markdown,
    render_def_list,
)


# Class
class FunctionRTLRender:
    """
    Define the renderer for the functions block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component internal functions.
        """

        # Do we have anything to render ?
        if len(comp.functions) == 0:
            return

        # Does the config specify us something ?
        if comp.render.internals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Functions", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Functions list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.functions)} element{"s" if len(comp.functions) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # The function is rendered as a "natural" notation.
        # For largest functions / specific usage, perhaps add a flag somewhere ?
        functions_elements = []
        functions_descriptions = []
        for function in comp.functions:

            # Function name
            function_name = nodes.term()
            function_name += nodes.inline(text="• ")
            function_name += nodes.strong(text=function.name)

            # Function parameters
            function_name += nodes.inline(text=" (")
            for i, argument in enumerate(function.func_inputs):
                if i > 0:
                    function_name += nodes.inline(text=", ")
                function_name += render_badge(
                    argument.name, BadgeColor.BLUE, outline=True
                )
            function_name += nodes.inline(text=") ")

            # Add the function returns
            function_name += nodes.inline(
                text="→ ", classes=["sd-text-muted", "sd-fw-bold"]
            )
            function_name += render_badge(
                f"Type: {function.func_outputs[0].hdl_type}",
                BadgeColor.CYAN,
                outline=True,
            )

            # Render the function description
            functions_desc = nodes.paragraph()
            if function.description:
                functions_desc += render_markdown(
                    function.description, comp.file.path, self.parent.base_doc
                )
            else:
                functions_desc += nodes.Text("-")

            # Append the elements to the list
            functions_elements.append(function_name)
            functions_descriptions.append(functions_desc)

        # Render the final list
        body += render_def_list(functions_elements, functions_descriptions)
