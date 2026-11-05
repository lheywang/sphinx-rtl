# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the structures section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component, Signal
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    render_def_list,
    render_markdown,
)


# Class
class StructureRTLRender:
    """
    Define the renderer for the structures block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component structures.
        """

        # Do we have anything to render ?
        if len(comp.structures) == 0:
            return

        # Does the config specify us something ?
        if comp.render.internals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Structures", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Structure list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.structures)} element{"s" if len(comp.structures) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # For each structure, let's render a dropdown :
        for structure in comp.structures:

            structure_title = nodes.paragraph()
            structure_title += nodes.Text(structure.name)
            structure_title += nodes.inline(" ", " ")
            structure_title += render_badge(
                f"{len(structure.signals)} element{"s" if len(structure.signals) > 1 else ""}",
                BadgeColor.CYAN,
            )

            structure_dd, structure_body = render_dropdown(
                structure_title, is_open=False
            )
            body += structure_dd

            # Now, let's add the description :
            structure_desc = nodes.paragraph()
            structure_desc += render_markdown(
                structure.description, comp.file.path, self.parent.base_doc
            )

            # Add the elements to the structure
            structure_elements = []
            structure_descriptions = []
            for signal in structure.signals:

                signal_name = nodes.term()
                signal_name += nodes.inline(text="• ")
                signal_name += nodes.strong(text=signal.name)
                signal_name += nodes.inline(" ", " ")

                # Handle signal type
                signal_name += render_badge(signal.hdl_type, BadgeColor.CYAN)
                signal_name += nodes.inline(" ", " ")

                # Handle signal size
                signal_size = ""
                for begin, end in zip(signal.hdl_size[::2], signal.hdl_size[1::2]):
                    if not begin == end:
                        signal_size = signal_size + f"[{begin} : {end}]"
                if len(signal_size) == 0:
                    signal_size = "-"
                signal_name += render_badge(signal_size, BadgeColor.GREEN, outline=True)

                signal_description = nodes.paragraph()
                signal_description += render_markdown(
                    signal.description, comp.file.path, self.parent.base_doc
                )

                # Add the elements to the list
                structure_elements.append(signal_name)
                structure_descriptions.append(signal_description)

            # Add the main part to the dropdown
            structure_body += structure_desc

            # Render the signal list
            structure_body += render_def_list(
                structure_elements, structure_descriptions
            )
