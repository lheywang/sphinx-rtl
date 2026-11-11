# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    11/11/2026
#
# Brief :   CLI Configuration file
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import ComponentConfig, RTLConfig, Component

# Configure the project
rtl_config = RTLConfig()
rtl_config.configure_shown_elements()
rtl_config.configure_resolution(modules=True)
rtl_config.add_public_output("db.json")
rtl_config.add_public_output("backup/db_bckp.json")
rtl_config.add_private_output("db_nda.json")
rtl_config.add_component_source("../examples/db_nda.json")

# Let's also configure the components
comp_config = ComponentConfig()
comp_config.set_toolchain(
    "Altera MAX10", "Intel Quartus Prime Standard 24.1", "Verilator 5.0.55"
)
comp_config.set_status("Active", "", "Issue #9999")


# And why not defining a custom clean up function ?
def custom_cleanup(database):
    """
    Let's define a custom function, which is simpler than the default version
    """
    for component in database.values():

        # Clear internals
        component.signals.clear()
        component.modules.clear()

        # Reset file infos and parameters
        component.config = ComponentConfig()
        component.render = RTLConfig()
