# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    09/10/2026
#
# Brief :   Implement the RTLTransform class, to act as the render engine.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from pathlib import Path
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx_rtl.nodes import RTLPlaceholderNode
from sphinx_rtl.models import Component, FileInfo
from sphinx_rtl.RTLDomain import RTLDomain
from sphinx_rtl.RTLRender import RTLRender

# Configure logger
logger = logging.getLogger(__name__)


# Class
class RTLRenderTransform(SphinxPostTransform):
    """
    Implement the Sphinx post transform to be done once all the analysis was done.
    """

    default_priority = 5

    def run(self, **kwargs) -> None:
        """
        Perform the rendering pass
        """

        # Logs
        logger.info(f"[INFO] Executing the render on {self.env.docname}")

        # Fetch elements
        domain: RTLDomain = self.env.get_domain("rtl")  # type: ignore
        components = domain.data.get("components", {})

        placeholders = list(self.document.findall(RTLPlaceholderNode))
        for placeholder in placeholders:

            name = placeholder["component_name"]
            data = components.get(name, Component(FileInfo()))

            # Fetch the render engine
            render = RTLRender()
            rendered_nodes, refs = render.render(data, placeholder["base_doc"])

            # Add the references to the domain
            domain.add_symbol_batch(refs, self.env.docname)

            # Add some logs
            count = len(list(rendered_nodes.findall()))
            logger.info(f"[INFO] Rendered {name.strip()} ({count} nodes)")

            # Replace ourselves
            placeholder.replace_self(rendered_nodes)

        # Do we have any images to render ?
        # If yes, include them in the Sphinx image collector.
        # That a cost of our architecture, otherwise this would be done automatically after the reading pass.
        for img in self.document.findall(nodes.image):
            uri = img.get("uri", "")

            # Ignore remote path
            if uri.startswith(("http://", "https://", "data:")):
                continue

            # Is the file already known ?
            dest_name = Path(uri).name
            if uri not in self.env.images:
                self.env.images[uri] = ({self.env.docname}, dest_name)
            else:
                self.env.images[uri].add(self.env.docname)  # type: ignore

            # Note the dependency
            resolved_path = Path(self.env.srcdir) / uri
            if resolved_path.is_file():
                self.env.note_dependency(str(resolved_path.resolve()))
