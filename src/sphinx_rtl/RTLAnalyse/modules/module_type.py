# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Infer the type of the module
# ----------------------------------------------------------------------------

# Imports
from ...models import Component

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_type(component: Component) -> Component:
    """
    Try to guess the module type.
    """

    # Does the component is already tagged ?
    if component.config.isTestbench:
        component.comp_type = "testbench"
        logger.info(f"[INFO] Detected type : testbench")
        return component
    elif component.config.isPackage:
        component.comp_type = "package"
        logger.info(f"[INFO] Detected type : package")
        return component
    elif component.config.isInterface:
        component.comp_type = "interface"
        logger.info(f"[INFO] Detected type : interface")
        return component

    # First, fetch the number of different modules
    ports_count = len(component.ports)
    interface_count = len(component.interfaces)
    modules_count = len(component.modules)
    parameter_count = len(component.parameters)
    enums_count = len(component.enums)
    signal_count = len(component.signals)

    # A testbench or a package could not have any ports
    if ports_count == 0:

        # An empty port with no interface and some signals really look like a testbench !
        if (modules_count > 0) and (interface_count == 0) and (signal_count > 0):
            component.config.isTestbench = True
            component.comp_type = "testbench"
            logger.info(f"[INFO] Flagged type : testbench")

        elif ((enums_count > 0) or (parameter_count > 0)) and (signal_count == 0):
            component.config.isPackage = True
            component.comp_type = "package"
            logger.info(f"[INFO] Flagged type : package")

    else:

        # An interface could not have any modules in it...
        if (modules_count == 0) and (interface_count > 0):
            component.config.isInterface = True
            component.comp_type = "interface"
            logger.info(f"[INFO] Flagged type : interface")

        else:
            component.comp_type = "module"
            logger.info(f"[INFO] Flagged type : module")

    return component
