# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Define the render module, to transform Components into
#           Sphinx docutils node syntax.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx.util import logging
from pathlib import Path
from docutils.nodes import make_id
import itertools

from .helpers import (
    render_table_header,
    render_table_line,
    render_snippet,
    render_badge,
    BadgeColor,
    render_dropdown,
    render_markdown,
    render_ref,
    use_ref,
    render_bullet_list,
    render_def_list,
    render_flex_array,
)
from ..models import Component, Signal

# Configure the logger
logger = logging.getLogger(__name__)


class RTLRender:
    """
    Render a passed component into docutils nodes.
    """

    # --------------------------------------------------------------------------------
    # BUILTINS
    # --------------------------------------------------------------------------------

    def __init__(self):
        """
        Init the render class
        """

        # Set the base doc to use
        self.base_doc = Path(__file__)

        # Build the reference base list
        self.refs: list[dict] = []

        return

    # --------------------------------------------------------------------------------
    # PUBLIC FUNCTIONS
    # --------------------------------------------------------------------------------

    def render(
        self, component: Component | None, base_doc: Path
    ) -> tuple[list[nodes.container], list[dict]]:
        """
        Render a component into an AST of nodes.

        This function is the generic entry, and will call the correct function as well as creating the root component.
        For a more specific render, you can call :
            - render_as_package
            - render_as_module
            - render_as_testbench
            - render_as_module.

        This is, however not really recommended as this could lead with missing elements for a module.
        """

        # First, fetch our root node :
        root = nodes.container(is_div=True, classes=["rtl-component-view"])

        if component is None:
            logger.error("Provided component is None. Could not render anything.")
            return ([root], self.refs)

        # Update the base doc
        self.base_doc = base_doc

        # Now, we can safely render the component.
        # Any option will be valid, regardless of it's composition.
        match component.comp_type:
            case "module":
                logger.info(
                    f"[INFO] Rendering {f'{component.name} ' if component.name != "" else ""}as a module."
                )
                return self.render_as_module(component=component, root=root)

            case "testbench":
                logger.info(
                    f"[INFO] Rendering {f'{component.name} ' if component.name != "" else ""}as a testbench."
                )
                return self.render_as_testbench(component=component, root=root)

            case "package":
                logger.info(
                    f"[INFO] Rendering {f'{component.name} ' if component.name != "" else ""}as a package."
                )
                return self.render_as_package(component=component, root=root)

            case "interface":
                logger.info(
                    f"[INFO] Rendering {f'{component.name} ' if component.name != "" else ""}as an interface."
                )
                return self.render_as_interface(component=component, root=root)

        # Return the default value is nothing was found.
        return ([root], self.refs)

    def render_as_package(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[dict]]:
        """
        Render the provided component as a package.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name
        context = self._create_section(root, context_name)

        # Common module header
        self._render_file_info(context, component)

        # Add the elements we need here.
        self._render_component_imports(context, component)
        self._render_component_parameters(context, component)
        self._render_component_enums(context, component)
        self._render_component_functions(context, component)
        self._render_component_structures(context, component)

        # Add a separator last
        self._add_separator(context)

        # Return the global node
        return ([root], self.refs)

    def render_as_module(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[dict]]:
        """
        Render the provided component as a module.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name
        context = self._create_section(root, context_name)

        # Common module header
        self._render_file_info(context, component)

        # Add the elements we need here.
        self._render_component_imports(context, component)
        self._render_component_parameters(context, component)
        self._render_component_ports(context, component)
        self._render_component_enums(context, component)
        self._render_component_modules(context, component)
        self._render_component_processes(context, component)
        self._render_component_signals(context, component)
        self._render_component_assigns(context, component)

        # Add a separator last
        self._add_separator(context)

        # Return the global node
        return ([root], self.refs)

    def render_as_testbench(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[dict]]:
        """
        Render the provided component as a testbench.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name
        context = self._create_section(root, context_name)

        # Common module header
        self._render_file_info(context, component)

        # Add a separator last
        self._add_separator(context)

        # Add the elements we need here.
        self._render_component_imports(context, component)
        self._render_component_parameters(context, component)
        self._render_component_signals(context, component)
        self._render_component_modules(context, component)
        self._render_component_processes(context, component)

        # Return the global node
        return ([root], self.refs)

    def render_as_interface(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[dict]]:
        """
        Render the provided component as an interface.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name

        context = self._create_section(root, context_name)

        # Common module header
        self._render_file_info(context, component)

        # Add the elements we need here.
        self._render_component_imports(context, component)
        self._render_component_parameters(context, component)
        self._render_component_ports(context, component)
        self._render_component_interfaces(context, component)

        # Add a separator last
        self._add_separator(context)

        # Return the global node
        return ([root], self.refs)

    # --------------------------------------------------------------------------------
    # PRIVATE FUNCTIONS
    # --------------------------------------------------------------------------------

    def _render_file_info(self, root: nodes.section, comp: Component) -> None:
        """
        Render the file info blob as a clean area on top of the page.

        Add the module name, and a flag depending on it's type.
        If available, git information will also be added for both the latest edit and the initial creation.

        Must be called first, as it will add a section title and a separator
        """

        # Build the card first
        card = nodes.container(
            is_div=True, classes=["sd-card", "sd-shadow-sm", "sd-mb-3"]
        )

        # First, add the file name
        card_header = nodes.container(
            is_div=True,
            classes=[
                "sd-card-header",
                "sd-py-2",
                "sd-px-3",
                "sd-d-flex-row",
                "sd-align-major-justify",
            ],
        )

        # Module name
        title_box = nodes.paragraph(classes=["sd-m-0"])
        title_box += nodes.strong(
            text=comp.file.name.rsplit(".", 1)[0], classes=["sd-fs-5"]
        )
        title_box += nodes.inline(" ", " ")

        # Module type
        color = BadgeColor.GREEN
        match comp.comp_type:
            case "module":
                color = BadgeColor.GREEN
            case "testbench":
                color = BadgeColor.BLUE
            case "package":
                color = BadgeColor.ORANGE
            case "interface":
                color = BadgeColor.CYAN

        title_box += render_badge(comp.comp_type, color=color, outline=True, pill=True)
        card_header += title_box

        if len(comp.render.vendor) > 0:
            vendor_box = nodes.paragraph(classes=["sd-m-0"])
            for vendor in comp.render.vendor:
                vendor_box += render_badge(
                    vendor, color=BadgeColor.RED, outline=True, pill=True
                )
                vendor_box += nodes.inline(" ", " ")
            card_header += vendor_box

        card += card_header

        # Component description
        # First, add the file name
        card_description = nodes.container(
            is_div=True,
            classes=[
                "sd-card-header",
                "sd-d-flex",
                "sd-align-major-justify",
                "sd-align-minor-center",
            ],
        )

        desc_box = nodes.paragraph(classes=["sd-m-0", "sd-fw-semibold"])
        desc_box += render_markdown(comp.brief, comp.file.path, self.base_doc)
        card_description += desc_box
        detail_box = nodes.paragraph(classes=["sd-mt-1", "sd-text-muted", "sd-small"])
        detail_box += render_markdown(comp.details, comp.file.path, self.base_doc)
        card_description += detail_box

        card += card_description

        # Now, add the different elements about the file status
        # This may be dependant on the git status, so :

        footer = nodes.container(
            is_div=True,
            classes=[
                "sd-card-footer",
                "sd-py-2",
                "sd-px-3",
                "sd-fs-7",
                "sd-text-muted",
            ],
        )

        last_block = nodes.container(is_div=True, classes=["sd-m-2"])

        row_author = nodes.container(
            is_div=True,
            classes=[
                "sd-d-flex-row",
                "sd-align-major-justify",
                "sd-align-minor-center",
            ],
        )

        author = nodes.paragraph(classes=["sd-m-0", "sd-fw-semibold"])
        author += nodes.Text(comp.file.edit_author)
        row_author += author

        date = nodes.paragraph(classes=["sd-m-0"])
        date += nodes.Text(comp.file.edit_date)
        row_author += date

        # Add that to the current row
        last_block += row_author

        # If the fileInfo class does know some things about git, let's add tem
        if comp.file.edit_hash != "":

            badges = nodes.paragraph(classes=["sd-m-0", "sd-my-1"])
            badges += render_badge(
                f"Tag : {comp.file.edit_tag}", color=BadgeColor.ORANGE, outline=True
            )
            badges += nodes.inline(" ", " ")
            hash_badge = render_badge(
                f"Hash : {comp.file.edit_hash}", color=BadgeColor.CYAN, outline=True
            )
            hash_badge["classes"].append("code")
            badges += hash_badge
            badges += nodes.inline(" ", " ")

            dirty_color = BadgeColor.RED if comp.file.is_dirty else BadgeColor.GREEN
            dirty_msg = "Dirty build" if comp.file.is_dirty else "Clean build"
            badges += render_badge(dirty_msg, dirty_color, outline=True)

            last_block += badges

            # Add the commit message
            commit = nodes.paragraph(classes=["sd-m-0", "sd-fst-italic"])
            commit += nodes.Text(f"Commit message : <{comp.file.message}>")
            last_block += commit

        # Add the block to the root
        footer += last_block

        # Add the creation block (only available with git integration)
        if comp.file.creation_hash != "":

            initial_block = nodes.container(
                is_div=True,
                classes=["sd-m-2"],
            )

            row_in_author = nodes.container(
                is_div=True,
                classes=[
                    "sd-d-flex-row",
                    "sd-align-major-justify",
                    "sd-align-minor-center",
                ],
            )

            in_author = nodes.paragraph(classes=["sd-m-0", "sd-fw-semibold"])
            in_author += nodes.Text(f"Initial Author : {comp.file.creation_author}")
            row_in_author += in_author

            in_date = nodes.paragraph(classes=["sd-m-0"])
            in_date += nodes.Text(comp.file.creation_date)
            row_in_author += in_date

            # Add that to the current row
            initial_block += row_in_author

            badges = nodes.paragraph(classes=["sd-m-0", "sd-my-1"])
            badges += render_badge(
                f"Tag : {comp.file.creation_tag}", color=BadgeColor.ORANGE, outline=True
            )
            badges += nodes.inline(" ", " ")
            hash_badge = render_badge(
                f"Hash : {comp.file.creation_hash}", color=BadgeColor.CYAN, outline=True
            )
            hash_badge["classes"].append("code")
            badges += hash_badge

            initial_block += badges

            # Add the block to the root
            footer += initial_block

        # Add the footer to the card
        card += footer

        # Finally add ourselves to the root
        root += card
        return

    def _render_component_imports(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component imports
        """
        # Do we have anything to render ?
        if len(comp.imports) == 0:
            return

        # First, build the section we need
        section = self._create_section(
            root, "Imports", comp.file.name.rsplit(".", 1)[0]
        )

        # For each import, render it under the form of the source library and a list of nodes.
        elements = []
        count = 0
        for imported in comp.imports:

            line = nodes.paragraph()
            line += render_ref(imported.library, comp.name, "import", self.refs)
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

    def _render_component_parameters(
        self, root: nodes.section, comp: Component
    ) -> None:
        """
        Render a component parameters.
        """

        # Do we have anything to render ?
        if len(comp.parameters) == 0:
            return

        # First, build the section we need
        section = self._create_section(
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
            element += render_ref(parameter.name, comp.name, "parameter", self.refs)
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
                    parameter.description, comp.file.path, self.base_doc
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

    def _render_component_ports(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component ports as grouped by the system
        """

        # Do we have anything to render ?
        if len(comp.ports) == 0:
            return

        # First, build the section we need
        section = self._create_section(root, "Ports", comp.file.name.rsplit(".", 1)[0])

        # Build the master title
        title = nodes.paragraph()
        title += nodes.Text("Ports list")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(comp.ports)} element{"s" if len(comp.ports) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # Then, build the master dict. For each port, we'll seek for it's name later and render the port
        groups = dict()

        # At first, we'll need the default dropdown
        dd, body = render_dropdown(title, is_open=True)
        section += dd

        # Into the body, let's add a table
        headers = [
            "Name",
            "Direction",
            "Description",
            "Type",
            "Size",
            "Kind",
            "Polarity",
        ]
        widths = [1, 3, 3, 1, 2, 2, 1]

        table_body, table = render_table_header(headers, widths=widths)
        body += table_body

        # Add the current table into the element.
        groups[""] = dict()
        groups[""]["body"] = body
        groups[""]["table"] = table

        # Init clocks elements
        clocks_colors = [
            BadgeColor.RED,
            BadgeColor.CYAN,
            BadgeColor.GREEN,
            BadgeColor.BLUE,
        ]
        current_clock_color = -1
        resets_colors = [
            BadgeColor.RED,
            BadgeColor.CYAN,
            BadgeColor.GREEN,
            BadgeColor.BLUE,
        ]
        current_reset_color = -1

        # Init clocks and resets dict
        clocks = dict()
        resets = dict()

        # Build a raw group array to count element
        raw_groups = []
        for x in comp.ports:
            raw_groups.extend(x.group.split("/"))

        # First, create the list of groups.
        for port in comp.ports:
            port_groups = port.group.split("/")
            for group in port_groups:

                # Is the group known to us ?
                if not group in groups.keys():

                    # Fetch the index
                    group_index = port_groups.index(group)

                    # Let's add another dropdown element to it !
                    group_title = nodes.paragraph()
                    group_title += nodes.Text(group)
                    group_title += nodes.inline(" ", " ")

                    # Count how many element do we have in the group
                    count = raw_groups.count(group)
                    if count > 0:
                        group_title += render_badge(
                            f"{count} element{"s" if count > 1 else ""}",
                            BadgeColor.CYAN,
                        )

                    # Add a dropdown
                    group_dd, group_body = render_dropdown(group_title)

                    # Add a table inside ourselves
                    group_table_body, group_table = render_table_header(headers)
                    group_body += group_table_body

                    # Add the current table into the element.
                    # Are we the single port, or shall we append us to the previous element ?
                    if group_index > 0:

                        # Add ourselves to the our group name
                        groups[group] = dict()
                        groups[group]["body"] = group_body
                        groups[group]["table"] = group_table

                        # Add ourselves to our parent
                        groups[port_groups[group_index - 1]]["body"] += group_dd

                    # Else add to the root port
                    else:
                        groups[group] = dict()
                        groups[group]["body"] = group_body
                        groups[group]["table"] = group_table
                        groups[""]["body"] += group_dd

        for port in comp.ports:
            # Group does now match the latest element of it
            group = port.group.split("/")[-1]

            # Prepare the render elements
            port_name = nodes.paragraph()
            port_name += render_ref(port.name, comp.name, "port", self.refs)
            port_name += nodes.Text(port.name.strip())
            port_desc = render_markdown(port.description, comp.file.path, self.base_doc)
            port_type = nodes.literal(text=port.hdl_type.strip())

            # Extract the description as a docutils nodes

            # Handle port direction
            match port.direction:
                case "input":
                    port_dir = render_badge("Input", BadgeColor.GREEN, outline=True)
                case "output":
                    port_dir = render_badge("Output", BadgeColor.BLUE, outline=True)
                case _:
                    port_dir = render_badge("Input", BadgeColor.ORANGE, outline=True)

            # Handle port polarity
            match port.hdl_polarity:
                case "negative":
                    port_pol = render_badge("Negative", BadgeColor.RED, outline=True)
                case _:
                    port_pol = nodes.Text("-")

            # Handle port size
            port_size = nodes.paragraph()
            for begin, end in zip(port.hdl_size[::2], port.hdl_size[1::2]):
                if not begin == end:
                    port_size += nodes.literal(text=f"[{begin} : {end}]")
                    port_size += nodes.inline(" ", " ")
            if len(port_size) == 0:
                port_size += nodes.Text("-")

            # Handle port direction and clocking
            if len(port.hdl_sync) == 0:
                port_out_type = render_badge("Combinatorial", BadgeColor.GREEN)
            else:
                port_out_type = render_badge("Register", BadgeColor.ORANGE)

                # Add the matching clock name here
                port_clock = clocks.get(port.hdl_sync[0])
                if port_clock is None:
                    clocks[port.hdl_sync[0]] = render_badge(
                        port.hdl_sync[0], clocks_colors[current_clock_color]
                    )
                    current_clock_color -= 1
                    port_clock = clocks.get(port.hdl_sync[0])

                # Add the clock
                if port_clock is not None:
                    port_out_type += nodes.inline(" ", " ")
                    port_out_type += port_clock

            # Do we have a reset to add ?
            if len(port.hdl_reset) > 0:
                port_reset = resets.get(port.hdl_reset[0])
                if port_reset is None:
                    resets[port.hdl_reset[0]] = render_badge(
                        port.hdl_reset[0], resets_colors[current_reset_color]
                    )
                    current_reset_color -= 1
                    port_reset = resets.get(port.hdl_reset[0])

                if port_reset is not None:
                    port_out_type += nodes.inline(" ", " ")
                    port_out_type += port_reset

            # Add ourselves to the line
            render_table_line(
                groups[group]["table"],
                [
                    port_name,
                    port_dir,
                    port_desc,
                    port_type,
                    port_size,
                    port_out_type,
                    port_pol,
                ],
            )

    def _render_component_modules(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component modules.
        """

        # Do we have anything to render ?
        if len(comp.modules) == 0:
            return

        # First, build the section we need
        section = self._create_section(
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

            module_title += nodes.Text(f"{module.entity} :")
            module_title += nodes.inline(" ", " ")

            if module.name:
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
                    module.description, comp.file.path, self.base_doc
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
                if source:

                    source_node = nodes.paragraph()
                    source_node += use_ref(
                        source,
                        module.entity,
                        "port",
                        render_badge(source, BadgeColor.GREEN, outline=True),
                        False,
                    )

                    row.append(source_node)

                if source and target:
                    row.append(nodes.strong(text=" <-> "))

                if target:

                    target_node = nodes.paragraph()
                    target_node += use_ref(
                        target,
                        comp.name,
                        target_type,
                        render_badge(target, BadgeColor.BLUE, outline=True),
                        False,
                    )

                    row.append(target_node)

                # Add the connection to the list
                connections_list.append(row)

            # Render the list
            module_body += render_flex_array(connections_list)

    def _render_component_processes(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component processes.
        """

        # Do we have anything to render ?
        if len(comp.process) == 0:
            return

        # First, build the section we need
        section = self._create_section(
            root, "Processes", comp.file.name.rsplit(".", 1)[0]
        )

    def _render_component_enums(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component enums
        """

        # Do we have anything to render ?
        if len(comp.enums) == 0:
            return

        # First, build the section we need
        section = self._create_section(root, "Enums", comp.file.name.rsplit(".", 1)[0])

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
            enum_title += render_ref(enum.name, comp.name, "enum", self.refs)
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
                    enum.description, comp.file.path, self.base_doc
                )

            enum_body += enum_description

            # Add the elements into it, as a list
            elements = []
            for member, value in zip(enum.members, enum.values):

                row = []
                value_name = nodes.paragraph()
                value_name += render_ref(member, comp.name, "enum-value", self.refs)
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

    def _render_component_structures(
        self, root: nodes.section, comp: Component
    ) -> None:
        """
        Render the component structures.
        """

        # Do we have anything to render ?
        if len(comp.structures) == 0:
            return

        # First, build the section we need
        section = self._create_section(
            root, "Structures", comp.file.name.rsplit(".", 1)[0]
        )

    def _render_component_functions(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component internal functions.
        """

        # Do we have anything to render ?
        if len(comp.functions) == 0:
            return

        # First, build the section we need
        section = self._create_section(
            root, "Functions", comp.file.name.rsplit(".", 1)[0]
        )

    def _render_component_signals(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component signals
        """

        # Do we have anything to render ?
        if len(comp.signals) == 0:
            return

        # First, build the section we need
        section = self._create_section(
            root, "Signals", comp.file.name.rsplit(".", 1)[0]
        )

    def _render_component_assigns(self, root: nodes.section, comp: Component) -> None:
        """
        Render the component static assignment.
        """

        # Do we have anything to render ?
        if len(comp.assigns) == 0:
            return

        # First, build the section we need
        section = self._create_section(
            root, "Assignments", comp.file.name.rsplit(".", 1)[0]
        )

    def _render_component_interfaces(
        self, root: nodes.section, comp: Component
    ) -> None:
        """
        Render the component interfaces.
        """

        # Do we have anything to render ?
        if len(comp.interfaces) == 0:
            return

        # First, build the section we need
        section = self._create_section(
            root, "Interfaces", comp.file.name.rsplit(".", 1)[0]
        )

    def _add_separator(self, root: nodes.section) -> None:
        """
        Add the final separator to the component.
        """

        divider = nodes.transition()
        root += divider

    def _create_section(
        self, root: nodes.container | nodes.section, name: str, id: str = ""
    ) -> nodes.section:
        """
        Create a section within the current context, and return it.
        """

        if id:
            section = nodes.section(ids=[make_id(f"{id}-{name}")])
        else:
            section = nodes.section(ids=[make_id(name)])
        section += nodes.title(text=name)
        section += render_ref(name, id, "", self.refs)
        root += section

        return section
