# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Initialize sphinx to find our module
# ----------------------------------------------------------------------------

# Imports
from .directive import RTLAutodocDirective


# Setup
def setup(app):

    # Load the extensions
    app.setup_extension("myst_parser")

    # Add the name and aliases
    app.add_directive("rtl-autodoc", RTLAutodocDirective)
    app.add_directive("vhdl-autodoc", RTLAutodocDirective)
    app.add_directive("sv-autodoc", RTLAutodocDirective)

    # Return
    return {"version": "0.1.0", "parallel_read_safe": True, "parallel_write_safe": True}
