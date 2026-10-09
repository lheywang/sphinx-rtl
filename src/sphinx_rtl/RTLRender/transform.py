# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    09/10/2026
#
# Brief :   Implement the RTLTransform class, to act as the render engine.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx_rtl.nodes import RTLPlaceholderNode
from sphinx_rtl.models import Component, FileInfo

# Configure logger
logger = logging.getLogger(__name__)


# Class
class RTLRenderTransform(SphinxPostTransform):
    """
    Implement the Sphinx post transform to be done once all the analysis was done.
    """

    default_priority = 500

    def run(self, **kwargs) -> None:
        """
        Perform the rendering pass
        """

        # Logs
        logger.info(f"[INFO] Executing the render on {self.env.docname}")

        # Fetch elements
        domain = self.env.get_domain("rtl")
        components = domain.data.get("components", {})

        placeholders = list(self.document.findall(RTLPlaceholderNode))
        for placeholder in placeholders:

            name = placeholder["component_name"]
            data = components.get(name, Component(FileInfo()))

            logger.info(f"[INFO] Rendering {name}")

            # Replace ourselves
            placeholder.replace_self([nodes.paragraph()])
