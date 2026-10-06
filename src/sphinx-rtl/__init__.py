# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Initialize sphinx to find our module
# ----------------------------------------------------------------------------

# Imports
from sphinx.application import Sphinx
from pathlib import Path

from .directive import RTLAutodocDirective
from .RTLDomain import RTLDomain


# Setup
def setup(app):

    # Load the extensions
    app.setup_extension("myst_parser")
    app.setup_extension("sphinx_design")

    # Add the domain
    app.add_domain(RTLDomain)

    # Add the custom CSS we need to inject
    static_dir = Path(__file__).parent / "static"

    # Custom hook to add the file when the user does build
    def add_static_path(app: Sphinx) -> None:
        app.config.html_static_path.append(str(static_dir))

    # Register it
    app.connect("builder-inited", add_static_path)
    app.add_css_file("rtl.css")

    # Add the name and aliases
    app.add_directive("rtl-autodoc", RTLAutodocDirective)
    app.add_directive("vhdl-autodoc", RTLAutodocDirective)
    app.add_directive("sv-autodoc", RTLAutodocDirective)

    # Return
    return {"version": "0.1.0", "parallel_read_safe": True, "parallel_write_safe": True}
