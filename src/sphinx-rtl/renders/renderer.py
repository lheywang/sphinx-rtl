# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Define the render module, to transform Components into
#           Sphinx docutils node syntax.
# ----------------------------------------------------------------------------

# Imports
from collections import defaultdict
from docutils import nodes
from sphinx.util import logging

from .helpers import render_table, render_snippet, render_badge, BadgeColor
from ..models import Component, FileInfo

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
        return

    # --------------------------------------------------------------------------------
    # PUBLIC FUNCTIONS
    # --------------------------------------------------------------------------------

    def render(
        self, component: Component | None
    ) -> tuple[list[nodes.container], list[str]]:
        """
        Render a component into an AST of nodes.
        """

        # First, fetch our root node :
        root = nodes.container(is_div=True, classes=["rtl-component-view"])

        if component is None:
            logger.error("Provided component is None. Could not render anything.")
            return ([root], [""])

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
        return ([root], [""])

    def render_as_package(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[str]]:
        """
        Render the provided component as a package.
        """
        self._render_file_info(root, component)
        return ([root], [""])

    def render_as_module(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[str]]:
        """
        Render the provided component as a module.
        """
        self._render_file_info(root, component)
        return ([root], [""])

    def render_as_testbench(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[str]]:
        """
        Render the provided component as a testbench.
        """
        self._render_file_info(root, component)
        return ([root], [""])

    def render_as_interface(
        self, root: nodes.container, component: Component
    ) -> tuple[list[nodes.container], list[str]]:
        """
        Render the provided component as an interface.
        """
        self._render_file_info(root, component)
        return ([root], [""])

    # --------------------------------------------------------------------------------
    # PRIVATE FUNCTIONS
    # --------------------------------------------------------------------------------

    def _render_file_info(self, root: nodes.container, comp: Component) -> None:
        """
        Render the file info blob as a clean area on top of the page.
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
        desc_box += nodes.Text(comp.brief)
        card_description += desc_box
        detail_box = nodes.paragraph(classes=["sd-mt-1", "sd-text-muted", "sd-small"])
        detail_box += nodes.Text(comp.details)
        card_description += detail_box

        card += card_description

        # Finally add ourselves to the root
        root += card
        return
