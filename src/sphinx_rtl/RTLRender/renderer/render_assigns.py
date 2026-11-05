# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the assigns section of the page.
# ----------------------------------------------------------------------------

# Imports
import itertools

from docutils import nodes

from sphinx_rtl.models import Component, Signal
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    use_ref,
    render_dropdown,
    render_markdown,
    render_def_list,
)


# Class
class AssignRTLRender:
    """
    Define the renderer for the assigns block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component static assignment.
        """

        # Do we have anything to render ?
        if len(comp.assigns) == 0:
            return

        # Does the config specify us something ?
        if comp.render.internals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Assignments", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Assignment list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.assigns)} element{"s" if len(comp.assigns) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # Fetch the connections names
        connections = dict()
        for x in itertools.chain(comp.signals, comp.ports):
            connections[x.name] = x

        # Allocate memory and render the assignments.
        element_list = []
        description_list = []
        for assign in comp.assigns:

            # Add the constant elements.
            target_obj = connections.get(assign.target)
            target_type = "port"
            if target_obj is not None and type(target_obj) is Signal:
                target_type = "signal"

            target = nodes.term()
            target += nodes.inline(text="• ")
            target += use_ref(
                assign.target,
                comp.name,
                target_type,
                render_badge(assign.target, BadgeColor.CYAN, outline=True),
                False,
            )
            target += nodes.inline(" ", " ")
            target += render_badge(
                "Combinatorial" if assign.isComb else "Constant",
                BadgeColor.ORANGE if assign.isComb else BadgeColor.GREEN,
                outline=True,
            )

            # Add the description
            description = nodes.paragraph()

            if assign.description:
                description += render_markdown(
                    assign.description, comp.file.path, self.parent.base_doc
                )
                description += nodes.inline("<br>", "<br>")

            description += nodes.strong(
                text=f"Source{"s" if len(assign.source) > 1 else ""} : "
            )

            for source in assign.source:
                source_obj = connections.get(source)
                source_type = "port"
                if source_obj is not None and type(source_obj) is Signal:
                    source_type = "signal"

                description += use_ref(
                    source,
                    comp.name,
                    source_type,
                    render_badge(source, BadgeColor.BLUE, outline=True),
                    False,
                )
                description += nodes.inline(" ", " ")

            element_list.append(target)
            description_list.append(description)

        # render the list
        body += render_def_list(element_list, description_list)
