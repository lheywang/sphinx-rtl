# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Resolve the if there is any vendor primitives in the
#           design.
# ----------------------------------------------------------------------------

# Imports
import re
from ...models import Component
from .vendor_rules import classify_vendor

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_vendors(component: Component) -> Component:
    """
    Look for the different modules and identify if any vendors primitives are presents.
    """

    # Fetch the user defined vendors
    count = 0

    # Only the components (modules) could be primitives :
    for module in component.modules:
        vendor = classify_vendor(module.entity)

        # Edit the entity
        if vendor is not None:
            module.vendor = vendor.value
            module.isVendor = True

            # Add the name into the main list
            if vendor.value not in component.render.vendor:
                component.render.vendor.append(vendor.value)

            # For logging
            count += 1
    # Add some logging
    if count > 0:
        logger.info(
            f"[INFO] Found {count} primitive{"s" if count > 1 else ""} that match known vendors : {component.vendors}"
        )

    return component
