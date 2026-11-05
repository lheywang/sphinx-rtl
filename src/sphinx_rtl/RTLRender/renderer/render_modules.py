# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the modules section of the page.
# ----------------------------------------------------------------------------

# Imports
import itertools

from docutils import nodes

from sphinx_rtl.models import Component, Signal
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    render_ref,
    render_markdown,
    use_ref,
    render_flex_array,
)


# Class
class ModuleRTLRender:
    """
    Define the renderer for the modules block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component modules.
        """

        # Do we have anything to render ?
        if len(comp.modules) == 0:
            return

        # Does the config specify us something ?
        if comp.render.internals == False:
            return

        # First, build the section we need
        section = self.parent.create_section(
            root, "Modules", comp.file.name.rsplit(".", 1)[0]
        )

        # Build the dropdown menu
        title = nodes.paragraph()
        title += nodes.Text("Modules")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.modules)} element{"s" if len(comp.modules) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # Fetch the connections names
        connections = dict()
        for x in itertools.chain(comp.signals, comp.ports):
            connections[x.name] = x

        # Render the modules
        for module in comp.modules:

            # Build another dropdown inside of it
            module_title = nodes.paragraph()
            module_title += nodes.inline(text="• ")

            module_title += nodes.Text(f"{module.entity} :")
            module_title += nodes.inline(" ", " ")

            if module.name:
                module_title += render_ref(
                    module.name, comp.name, "module", self.parent.refs
                )
                module_title += nodes.Text(module.name)
            else:
                module_title += nodes.Text("-")
            module_title += nodes.inline(" ", " ")

            # Render the badges if needed
            # Render the module repetition.
            if module.isRepeated:

                # May arrive that a loop is repeated a single time.
                plural = "s"
                if module.count.isdigit():
                    count = int(module.count)
                    if count == 1:
                        plural = ""

                module_title += render_badge(
                    f"Repeated {module.count} time{plural}", BadgeColor.GREEN
                )
                module_title += nodes.inline(" ", " ")

            # Maybe the module is under a condition
            if module.isConditionnal:
                module_title += render_badge(
                    f"Conditioned by {module.condition}",
                    BadgeColor.ORANGE,
                    outline=True,
                )
                module_title += nodes.inline(" ", " ")

            # Maybe the module is a vendor primitive ?
            if module.isVendor:
                module_title += render_badge(
                    module.vendor, BadgeColor.RED, outline=True
                )
                module_title += nodes.inline(" ", " ")

            # Render the dropdown
            module_dd, module_body = render_dropdown(module_title, is_open=False)
            body += module_dd

            # Now render the module advanced elements
            module_description = nodes.paragraph()
            if module.description:
                module_description += render_markdown(
                    module.description, comp.file.path, self.parent.base_doc
                )
            module_body += module_description

            # Finally, render the connections
            connection_msg = nodes.paragraph()
            connection_msg += nodes.strong(text="Connections : ")
            module_body += connection_msg

            connections_list = []
            for source, target in module.connections:

                row = []

                # Fetch the type of the target:
                target_obj = connections.get(target)
                target_type = "port"
                if target_obj is not None and type(target_obj) is Signal:
                    target_type = "signal"

                # Add it to the list
                # Errors could be done here, to check later
                if target:

                    target_node = nodes.paragraph()
                    target_node += use_ref(
                        target,
                        module.entity,
                        "port",
                        render_badge(target, BadgeColor.BLUE, outline=True),
                        False,
                    )

                    row.append(target_node)

                if source and target:
                    row.append(nodes.strong(text=" ⮂ "))

                if source:

                    source_node = nodes.paragraph()
                    source_node += use_ref(
                        source,
                        comp.name,
                        target_type,
                        render_badge(source, BadgeColor.GREEN, outline=True),
                        False,
                    )

                    row.append(source_node)

                # Add the connection to the list
                connections_list.append(row)

            # Render the list
            module_body += render_flex_array(connections_list)
