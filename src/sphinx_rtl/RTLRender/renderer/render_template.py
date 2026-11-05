# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/11/2026
#
# Brief :   Render the template code of the page.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes

from sphinx.util import logging

from sphinx_rtl.models import Component
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    render_raw_code,
    render_tabs,
)
from .instantiators import (
    INSTANCE_CALLBACKS,
    INSTANCE_LANGUAGES,
    PYGMENTS_INSTANCE_LANG,
)

# Configure the logger
logger = logging.getLogger(__name__)


# Class
class TemplateRTLRender:
    """
    Define the renderer for the template code block.
    """

    def __init__(self, parent):
        """
        Init the class. The parent must be a reference to the parent class 'self'.
        Used to access variables within the root.
        """
        self.parent = parent

    def render(self, root: nodes.section, comp: Component) -> None:
        """
        Render a component template, ready to be copied for adding the module into our design.
        """

        # Do the config say us something ?
        if comp.render.template == False:
            return

        # Create our section
        section = self.parent.create_section(
            root, "Instantiation templates", comp.file.name.rsplit(".", 1)[0]
        )

        # Create the title
        title = nodes.paragraph()
        title += nodes.Text("Instantiation templates")
        title += nodes.inline(" ", " ")

        # How many element do we have ?
        title += render_badge(
            f"{len(INSTANCE_LANGUAGES)} element{"s" if len(INSTANCE_LANGUAGES) > 1 else ""}",
            BadgeColor.CYAN,
            outline=True,
        )

        # Build a dropdown (default to hidden).
        # This let the page small enough to be read by humans.
        dd, body = render_dropdown(title, is_open=True)

        # Add a tabs elements into it
        tab_head, tab_elements = render_tabs(INSTANCE_LANGUAGES, group="RTL")

        # For each languages, fetch the current rendering
        for lang, tab in tab_elements.items():

            func = INSTANCE_CALLBACKS.get(lang)
            if func is None:
                tab += nodes.error(
                    f"The provided callbacks was not found for the language {lang}. This is a BUG. Fill and submit a report.",
                )
                continue

            # Now, call the function
            content = func(comp)

            # Fetch the color
            color_lang = PYGMENTS_INSTANCE_LANG.get(lang)
            if color_lang is None:

                # set a default value
                color_lang = "systemverilog"
                logger.warning(
                    f"Using default color rendering scheme (systemverilog) for {lang}"
                )

            # Add the the formatted code to the tab
            tab += render_raw_code(content, color_lang)

        body += tab_head

        # Add ourselves to the root
        section += dd
