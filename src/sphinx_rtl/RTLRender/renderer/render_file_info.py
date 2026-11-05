# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the file info section of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import BadgeColor, render_badge, render_markdown


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

        # Test : iterate over differences
        for diff in differences:

            # Identify the diff, and act as it
            match diff.name:

                case "warning":  # list[str]
                    pass

                case "notes":  # list[str]
                    pass

                case "version":  # str
                    pass

                case "task":  # str
                    pass

                case "constraints":  # list[str]
                    pass

                case "compliance":  # list[str]
                    pass

                case "security":  # str
                    pass

                case "clocks":  #  list[tuple[str, str, str]]
                    pass

                case "latency":  # int
                    pass

                case "throughput":  # int
                    pass

                case "burst":  # int
                    pass

                case "target":  # list[str]
                    pass

                case "tool":  # list[str]
                    pass

                case "sim":  # list[str]
                    pass

                case "license":  # list[str]
                    pass

                case "copyright":  # str
                    pass

                case "tags":  # list[str]
                    pass

        # Add the footer into the card header
        root += footer
