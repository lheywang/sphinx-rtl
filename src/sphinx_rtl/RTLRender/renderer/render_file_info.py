# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the file info section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_markdown,
    render_bullet_list,
)


# Class
class FileInfoRTLRender:
    """
    Define the renderer for the file informations block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
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

        # Is the component deprecated, add a class to identify it with the final CSS.
        if comp.config.deprecated:
            card["classes"].append("deprecated-card")

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
        title_box += nodes.strong(text=comp.name, classes=["sd-fs-5"])
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

        # Is the component deprecated ?
        if comp.config.deprecated:
            title_box += nodes.inline(" ", " ")
            title_box += render_badge(
                "Deprecated", color=BadgeColor.RED, outline=True, pill=True
            )

        # Has the component a status ?
        if comp.config.status:
            title_box += nodes.inline(" ", " ")
            title_box += render_badge(
                comp.config.status, color=BadgeColor.BLACK, outline=True, pill=True
            )

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

        if comp.config.deprecated:
            deprecation_card = nodes.container(
                is_div=True,
                classes=[
                    "sd-card-footer",
                    "sd-d-flex",
                    "sd-align-major-justify",
                    "sd-align-minor-center",
                ],
            )

            deprecation_msg = nodes.paragraph(classes=["sd-m-0", "sd-fw-semibold"])
            deprecation_msg += render_markdown(
                comp.config.deprecated, comp.file.path, self.parent.base_doc
            )

            # Add the box into the hierarchy
            deprecation_card += deprecation_msg
            card += deprecation_card

        # Component description
        # First, add the file name
        card_description = nodes.container(
            is_div=True,
            classes=[
                "sd-card-footer",
                "sd-d-flex",
                "sd-align-major-justify",
                "sd-align-minor-center",
            ],
        )

        desc_box = nodes.paragraph(classes=["sd-m-0", "sd-fw-semibold"])
        desc_box += render_markdown(comp.brief, comp.file.path, self.parent.base_doc)
        card_description += desc_box
        detail_box = nodes.paragraph(classes=["sd-mt-1", "sd-text-muted", "sd-small"])
        detail_box += render_markdown(
            comp.details, comp.file.path, self.parent.base_doc
        )
        card_description += detail_box

        card += card_description

        # Before pursuing, emit an event to enable
        self.parent.app.emit(
            "rtl-card-rendering", self.parent.app, self.parent.env, card, comp
        )

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

        # Render the configuration of the component, if needed:
        self._render_component_config(card, comp)

        # Add the footer to the card
        card += footer

        # Finally add ourselves to the root
        root += card
        return

    def _render_component_config(self, root: nodes.container, comp: Component) -> None:
        """
        Render the component configuration is there's things to be added !
        This is highly configurable, and may, or may not be useful everywhere.
        """

        # Fetch the differences
        differences = list(comp.config.iter_differences)

        # Did anything has changed ?
        if len(differences) == 0:
            return

        # Then, we can create the diff section
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

        # Build the section dict, and fetch them. This will make the rendering more ordered and cleaner.
        db: dict[str, nodes.container] = {}

        def get_or_create(
            db: dict[str, nodes.container], name: str, footer: nodes.container
        ) -> nodes.container:
            """
            Return a nodes.container within the provided database.
            If it cannot be found, create it.
            """

            # Does the target already exists ?
            target = db.get(name)
            if target is not None:
                return target

            # Create it
            db[name] = nodes.container(classes=["sd-mt-3"])
            db[name] += nodes.paragraph(classes=["sd-mt-2"])
            db[name] += nodes.strong(text=name)

            # Add it to the footer
            footer += db[name]
            return db[name]

        # Test : iterate over differences
        for diff in differences:

            # Identify the diff, and act as it
            match diff.name:

                case "warning":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Information", footer)
                    warning_paragraph = nodes.paragraph()
                    warning_paragraph += nodes.Text("Warnings")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for warn in comp.config.warning:

                        warn_paragraph = nodes.paragraph()
                        warn_paragraph += render_markdown(
                            warn, comp.file.path, self.parent.base_doc
                        )
                        elements.append(warn_paragraph)

                    warning_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += warning_paragraph

                case "notes":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Information", footer)
                    notes_paragraph = nodes.paragraph()
                    notes_paragraph += nodes.Text("Notes")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for note in comp.config.notes:
                        note_paragraph = nodes.paragraph()
                        note_paragraph += render_markdown(
                            note, comp.file.path, self.parent.base_doc
                        )
                        elements.append(note_paragraph)

                    notes_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += notes_paragraph

                case "constraints":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Information", footer)
                    constraints_paragraph = nodes.paragraph()
                    constraints_paragraph += nodes.Text("Constraints")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for constraint in comp.config.constraints:
                        constraint_paragraph = nodes.paragraph()
                        constraint_paragraph += render_markdown(
                            constraint, comp.file.path, self.parent.base_doc
                        )
                        elements.append(constraint_paragraph)

                    constraints_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += constraints_paragraph

                case "version":  # str

                    # Fetch the master container
                    container = get_or_create(db, "Information", footer)
                    version_paragraph = nodes.paragraph()
                    version_paragraph += nodes.Text("Version")
                    version_paragraph += nodes.inline(" ", " ")
                    version_paragraph += render_badge(
                        comp.config.version, BadgeColor.GREEN, outline=True
                    )

                    # Add ourselves to the container
                    container += version_paragraph

                case "task":  # str

                    # Fetch the master container
                    container = get_or_create(db, "Information", footer)
                    task_paragraph = nodes.paragraph()
                    task_paragraph += nodes.Text("Task")
                    task_paragraph += nodes.inline(" ", " ")
                    task_paragraph += render_badge(
                        comp.config.task, BadgeColor.ORANGE, outline=True
                    )

                    # Add ourselves to the container
                    container += task_paragraph

                case "compliance":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Information", footer)
                    compliances_paragraph = nodes.paragraph()
                    compliances_paragraph += nodes.Text("Compliance")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for compliance in comp.config.compliance:
                        compliance_paragraph = nodes.paragraph()
                        compliance_paragraph += render_markdown(
                            compliance, comp.file.path, self.parent.base_doc
                        )
                        elements.append(compliance_paragraph)

                    compliances_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += compliances_paragraph

                case "security":  # str

                    # Fetch the master container
                    container = get_or_create(db, "Information", footer)
                    security_paragraph = nodes.paragraph()
                    security_paragraph += nodes.Text("Security :")
                    security_paragraph += nodes.inline(" ", " ")
                    security_paragraph += render_badge(
                        comp.config.security, BadgeColor.RED, outline=True
                    )

                    # Add ourselves to the container
                    container += security_paragraph

                case "clock":  #  list[tuple[str, int, int, str]]

                    # Fetch the master container
                    container = get_or_create(db, "Hardware", footer)
                    clocks_paragraph = nodes.paragraph()
                    clocks_paragraph += nodes.Text("Clocks")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for clock in comp.config.clock:

                        clock_paragraph = nodes.paragraph()
                        clock_paragraph += render_badge(
                            clock[0], BadgeColor.GREEN, outline=True
                        )
                        clock_paragraph += nodes.inline(" ", " ")
                        clock_paragraph += render_badge(
                            clock[1], BadgeColor.BLUE, outline=True
                        )
                        elements.append(clock_paragraph)

                    clocks_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += clocks_paragraph

                case "latency":  # int

                    # Fetch the master container
                    container = get_or_create(db, "Hardware", footer)
                    latency_paragraph = nodes.paragraph()
                    latency_paragraph += nodes.Text("Latency :")
                    latency_paragraph += nodes.inline(" ", " ")
                    latency_paragraph += render_badge(
                        str(comp.config.latency), BadgeColor.BLUE, outline=True
                    )

                    # Add ourselves to the container
                    container += latency_paragraph

                case "throughput":  # str

                    # Fetch the master container
                    container = get_or_create(db, "Hardware", footer)
                    throughput_paragraph = nodes.paragraph()
                    throughput_paragraph += nodes.Text("Throughput :")
                    throughput_paragraph += nodes.inline(" ", " ")
                    throughput_paragraph += render_badge(
                        comp.config.throughput, BadgeColor.BLACK, outline=True
                    )

                    # Add ourselves to the container
                    container += throughput_paragraph

                case "burst":  # int

                    # Fetch the master container
                    container = get_or_create(db, "Hardware", footer)
                    throughput_paragraph = nodes.paragraph()
                    throughput_paragraph += nodes.Text("Burst :")
                    throughput_paragraph += nodes.inline(" ", " ")
                    throughput_paragraph += render_badge(
                        str(comp.config.burst), BadgeColor.BLACK, outline=True
                    )

                    # Add ourselves to the container
                    container += throughput_paragraph

                case "target":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Toolchain", footer)
                    targets_paragraph = nodes.paragraph()
                    targets_paragraph += nodes.Text("Target")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for target in comp.config.target:

                        target_paragraph = nodes.paragraph()
                        target_paragraph += render_markdown(
                            target, comp.file.path, self.parent.base_doc
                        )
                        elements.append(target_paragraph)

                    targets_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += targets_paragraph

                case "tool":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Toolchain", footer)
                    tools_paragraph = nodes.paragraph()
                    tools_paragraph += nodes.Text("Tools")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for tool in comp.config.tool:

                        tool_paragraph = nodes.paragraph()
                        tool_paragraph += render_markdown(
                            tool, comp.file.path, self.parent.base_doc
                        )
                        elements.append(tool_paragraph)

                    tools_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += tools_paragraph

                case "sim":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Toolchain", footer)
                    sims_paragraph = nodes.paragraph()
                    sims_paragraph += nodes.Text("Simulator")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for sim in comp.config.sim:

                        sim_paragraph = nodes.paragraph()
                        sim_paragraph += render_markdown(
                            sim, comp.file.path, self.parent.base_doc
                        )
                        elements.append(sim_paragraph)

                    sims_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += sims_paragraph

                case "license":  # list[str]

                    # Fetch the master container
                    container = get_or_create(db, "Source Control", footer)
                    licenses_paragraph = nodes.paragraph()
                    licenses_paragraph += nodes.Text("License")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for license in comp.config.license:

                        license_paragraph = nodes.paragraph()
                        license_paragraph += render_markdown(
                            license, comp.file.path, self.parent.base_doc
                        )
                        elements.append(license_paragraph)

                    licenses_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += licenses_paragraph

                case "copyright":  # str

                    # Fetch the master container
                    container = get_or_create(db, "Hardware", footer)
                    copyright_paragraph = nodes.paragraph()
                    copyright_paragraph += nodes.Text("Copyright :")
                    copyright_paragraph += nodes.inline(" ", " ")
                    copyright_paragraph += render_badge(
                        str(comp.config.burst), BadgeColor.BLACK, outline=True
                    )

                    # Add ourselves to the container
                    container += copyright_paragraph

                case "tags":  # list[str]

                    container = get_or_create(db, "Source Control", footer)
                    tags_paragraph = nodes.paragraph()
                    tags_paragraph += nodes.Text("Tags")

                    # Render the different elements as a list
                    elements: list[nodes.paragraph] = []
                    for tag in comp.config.tags:

                        tag_paragraph = nodes.paragraph()
                        tag_paragraph += render_markdown(
                            tag, comp.file.path, self.parent.base_doc
                        )
                        elements.append(tag_paragraph)

                    tags_paragraph += render_bullet_list(elements)

                    # Add ourselves to the container
                    container += tags_paragraph

        # Add the footer into the card header
        root += footer
