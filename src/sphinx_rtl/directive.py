# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the top level parsing directive for Sphinx
# ----------------------------------------------------------------------------

# Imports
import glob
import time

from pathlib import Path
from sphinx.util import logging
from sphinx._cli.util.colour import bold, blue
from docutils.parsers.rst import Directive, directives

from sphinx_rtl.RTLDomain import RTLDomain
from sphinx_rtl.RTLParser2 import RTLParser2, registry
from sphinx_rtl.nodes import RTLPlaceholderNode
from sphinx_rtl.models import RTLConfig, ComponentConfig

# Configure the logger
logger = logging.getLogger(__name__)


class RTLAutodocDirective(Directive):

    # Configure the base class
    required_arguments = 1
    optional_arguments = 0
    has_content = False

    # Configure the known options to be passed
    option_spec = {
        # Standard options
        "warning": directives.unchanged,
        "note": directives.unchanged,
        "target": directives.unchanged,
        "tool": directives.unchanged,
        "sim": directives.unchanged,
        "compliance": directives.unchanged,
        "security": directives.unchanged,
        "status": directives.unchanged,
        "deprecated": directives.unchanged,
        "task": directives.unchanged,
        "license": directives.unchanged,
        "copyright": directives.unchanged,
        "tag": directives.unchanged,
        # Render flags
        "noclocks": directives.flag,
        "noresets": directives.flag,
        "noio": directives.flag,
        "notype": directives.flag,
        "nopolarity": directives.flag,
        "nogroups": directives.flag,
        "nosource": directives.flag,
        "notemplate": directives.flag,
        "nosignals": directives.flag,
        "novendors": directives.flag,
        "vendor": directives.unchanged,
    }

    # Set the contextual menu.
    has_content = True

    # Build the functions

    def get_config(self) -> tuple[ComponentConfig, RTLConfig]:
        """
        Fetch the config from the options.
        """

        # Build the Component Config object
        cfg = ComponentConfig()
        cfg.warning.append(self.options.get("warning", ""))
        cfg.notes.append(self.options.get("notes", ""))
        cfg.target.append(self.options.get("target", ""))
        cfg.tool.append(self.options.get("tool", ""))
        cfg.sim.append(self.options.get("sim", ""))
        cfg.compliance.append(self.options.get("compliance", ""))
        cfg.security = self.options.get("security", "")
        cfg.status = self.options.get("status", "")
        cfg.deprecated = self.options.get("deprecated", "")
        cfg.task = self.options.get("task", "")
        cfg.license.append(self.options.get("license", ""))
        cfg.copyright = self.options.get("copyright", "")
        cfg.tags.append(self.options.get("tag", ""))

        # Build the RTLConfig object
        rtl = RTLConfig()

        # Note : Selection is inverted, as flags DISABLE the thing.
        rtl.inferClocks = "noclocks" not in self.options
        rtl.inferResets = "noresets" not in self.options
        rtl.inferIOs = "noios" not in self.options
        rtl.inferType = "notype" not in self.options
        rtl.inferPolarity = "nopolarity" not in self.options
        rtl.inferGroups = "nogroups" not in self.options
        rtl.showSource = "nosource" not in self.options
        rtl.template = "notemplate" not in self.options
        rtl.signals = "nosignals" not in self.options
        rtl.internals = "nointernals" not in self.options
        rtl.vendor.append(self.options.get("vendor", ""))

        # Return them
        return cfg, rtl

    def run(self):
        """
        New parser for v0.6.0 and higher.
        """

        # Fetch the settings
        env = self.state.document.settings.env
        docname = env.docname
        rtl_domain: RTLDomain = env.get_domain("rtl")

        # Fetch the config for the component
        cfg, render_dir = self.get_config()

        # Fetch the default config
        rtl_cfg: RTLConfig = env.config.rtl_config

        # Merge the config into the components
        render = render_dir.merge(rtl_cfg)

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

                # Update the component config
                component.render = render.merge(component.render)
                component.config = cfg.merge(component.config)

                # Register the component
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
