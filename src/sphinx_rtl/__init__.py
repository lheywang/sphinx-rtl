# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Initialize sphinx to find our module
# ----------------------------------------------------------------------------

# Imports
from sphinx.application import Sphinx
from pathlib import Path
from sphinx_rtl.nodes import RTLPlaceholderNode
from sphinx_rtl.RTLDomain import RTLDomain
from sphinx_rtl.RTLRender import RTLRenderTransform
from sphinx_rtl.directive import RTLAutodocDirective
from sphinx_rtl.callbacks import on_builder_inited, on_env_get_outdated, on_env_updated


# Setup
def setup(app):

    # Add the custom node
    app.add_node(RTLPlaceholderNode)

    # Load the extensions
    app.setup_extension("myst_parser")
    app.setup_extension("sphinx_design")

    # Add the domain
    app.add_domain(RTLDomain)

    # Register the callbacks
    app.connect("builder-inited", on_builder_inited)
    app.connect("env-get-outdated", on_env_get_outdated)
    app.connect("env-updated", on_env_updated)

    # Add the post transform
    app.add_post_transform(RTLRenderTransform)

    # Add the custom CSS file
    app.add_css_file("rtl.css")

    # Add the name and aliases
    app.add_directive("rtl-autodoc", RTLAutodocDirective)
    app.add_directive("vhdl-autodoc", RTLAutodocDirective)
    app.add_directive("sv-autodoc", RTLAutodocDirective)

    # Return
    return {"version": "0.1.0", "parallel_read_safe": True, "parallel_write_safe": True}
