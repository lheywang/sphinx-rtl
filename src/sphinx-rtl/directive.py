# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the top level parsing directive for Sphinx
# ----------------------------------------------------------------------------

# Imports
import glob
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import Directive

from .parsers import xVerilogParser, VHDLParser
from .models import Component

# Open the different parsers
xVerilogTool = xVerilogParser()
VHDLTool = VHDLParser()


class RTLAutodocDirective(Directive):

    # Configure the base class
    required_arguments = 1
    optional_arguments = 0
    has_content = False

    # Build the functions
    def run(self):

        # Fetch the settings
        env = self.state.document.settings.env

        # Fetch the absolute path
        search = Path(env.srcdir) / Path(self.arguments[0])

        # Look for all files that could match:
        if any(char in self.arguments[0] for char in ("*", "?", "[")):
            matches = [
                Path(p).resolve() for p in glob.glob(str(search), recursive=True)
            ]
        elif search.is_dir():
            matches = [
                p.resolve()
                for p in search.iterdir()
                if p.suffix.lower() in {".sv", ".v", ".vhd", ".vhdl"}
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
        rendered_nodes: list[nodes.Node] = []

        for match in matches:
            env.note_dependency(str(match))

            print("Processing ", match)

            # Call the matching parser :
            suffix = match.suffix.lower()
            if suffix in [".sv", ".v"]:
                component = None
                # rendered_nodes.extend(self._render(component))
            elif suffix in [".vhd", ".vhdl"]:
                component = None
                # rendered_nodes.extend(self._render(component))
            else:
                return self.state.reporter.error(
                    f"Unknown format ({suffix}) for {path}.",
                    line=self.lineno,
                )

        # Build the nodes from our RTL component:
        return rendered_nodes

    def _render(self, component: Component) -> list[nodes.Node]:
        sec_id = nodes.make_id(f"rtl-{component.name}")
        sec = nodes.section(ids=[sec_id])

        sec += nodes.title(text=f"Module : {component.name}")

        # Brief
        if component.brief:
            p_brief = nodes.paragraph()
            p_brief += nodes.strong(text="Brief : ")
            p_brief += nodes.Text(component.brief)
            sec += p_brief

        # TODO : Inject all the remaining details

        return [sec]
