# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the top level parsing directive for Sphinx
# ----------------------------------------------------------------------------

# Imports
import glob
import time
from sphinx.util import logging
from sphinx._cli.util.colour import bold, blue
from pathlib import Path
from docutils.parsers.rst import Directive
from sphinx_rtl.RTLDomain import RTLDomain
from sphinx_rtl.RTLParser2 import RTLParser2, registry
from sphinx_rtl.nodes import RTLPlaceholderNode

# Configure the logger
logger = logging.getLogger(__name__)


class RTLAutodocDirective(Directive):

    # Configure the base class
    required_arguments = 1
    optional_arguments = 0
    has_content = False

    # Build the functions

    def run(self):
        """
        New parser for v0.6.0 and higher.
        """

        # Fetch the settings
        env = self.state.document.settings.env
        docname = env.docname
        rtl_domain: RTLDomain = env.get_domain("rtl")

        # Fetch the patterns
        patterns = registry.get_all_extension()

        # Fetch the absolute path
        search = Path(env.srcdir) / Path(self.arguments[0])

        # Look for all files that could match:
        if any(char in self.arguments[0] for char in ("*", "?", "[")):
            matches = [
                Path(p).resolve() for p in glob.glob(str(search), recursive=True)
            ]
        elif search.is_dir():
            matches = [
                p.resolve() for p in search.iterdir() if p.suffix.lower() in patterns
            ]
        else:
            matches = [search.resolve()]

        # Sort the files
        matches = sorted(
            [p for p in matches if p.is_file()],
            key=lambda p: p.name.lower(),
        )

        # Exit if nothing was found
        if not matches:
            return [
                self.state.document.reporter.warning(
                    f"Could not find RTL file for the following pattern : {self.arguments[0]}",
                    line=self.lineno,
                )
            ]

        # Process all files
        rendered_nodes: list[RTLPlaceholderNode] = []

        # Default values
        component = None

        for match in matches:

            ts = time.time()

            ok = rtl_domain.register_file_to_doc(
                filepath=match, docname=docname, glob=str(search)
            )

            # If the file is already claimed, continue.
            if not ok:
                continue

            logger.info(bold(f"[INFO] --- Processing file : {str(match)}"))

            # Call the matching parser :
            parser = RTLParser2()
            components = parser.parse(match)

            # Add the component to the internal db
            for component in components.values():
                rtl_domain.add_component(component, docname)

                # Build the placeholder
                base_doc = str(Path(self.state.document["source"]).resolve().parent)
                if component is not None:
                    rendered_nodes.append(
                        RTLPlaceholderNode(name=component.name, base_doc=base_doc)
                    )
                else:
                    logger.warning(
                        f"Source file at {match} failed to generate a valid component."
                    )

            tt = time.time()
            logger.info(blue(f"Processed file in {(tt - ts) * 1000:.3f} ms."))

        # Return the rendered nodes
        return rendered_nodes
