# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the process section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_def_list,
    render_dropdown,
    render_markdown,
)


# Class
class ProcessRTLRender:
    """
    Define the renderer for the process block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component processes.
        """

        # Do we have anything to render ?
        if len(comp.process) == 0:
            return

        # Does the config specify us something ?
        if comp.render.internals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Processes", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Process list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.process)} element{"s" if len(comp.process) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # Render the processes. Each of them is under it's on a definition list.
        # A dropdown would be overkill here, as we don't really care about all signals ...
        process_id = 1
        process_elements = []
        process_definitions = []
        for process in comp.process:

            process_name = nodes.paragraph()
            process_name += nodes.inline(text="• ")

            # Give a name to the process if not done.
            # The generated name is a simple number, starting from 1.
            if process.name:
                process_name += nodes.strong(text=process.name)
            else:
                process_name += nodes.strong(text=f"Process {process_id}")
            process_name += nodes.inline(" ", " ")
            process_id += 1

            # Add nice badges for the process elements
            if process.hdl_type == "flipflop":
                process_name += render_badge("Clocked", BadgeColor.GREEN, outline=True)
                process_name += nodes.inline(" ", " ")
                process_name += render_badge(
                    f"Clocked by {process.hdl_clock[0]}", BadgeColor.BLUE
                )
                process_name += nodes.inline(" ", " ")
            else:
                process_name += render_badge(
                    "Combinatorial", BadgeColor.ORANGE, outline=True
                )
                process_name += nodes.inline(" ", " ")

            # Add the reset flag
            if process.hdl_reset:
                process_name += render_badge(
                    f"Reset by {process.hdl_reset[0]}", BadgeColor.BLUE
                )

            # Handle the description
            process_desc = nodes.description()
            if process.description:
                process_desc += render_markdown(
                    process.description, comp.file.path, self.parent.base_doc
                )
            else:
                process_desc += nodes.Text("-")

            # Add the elements to the list
            process_elements.append(process_name)
            process_definitions.append(process_desc)

        # Render the whole process as a list
        body += render_def_list(process_elements, process_definitions)
