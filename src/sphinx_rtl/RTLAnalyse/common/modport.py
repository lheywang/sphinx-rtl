# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    02/11/2026
#
# Brief :   Bind information fetched from other elements to the modport.
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import Component, Signal

# Configure logger
from sphinx.util import logging
from sphinx._cli.util.colour import blue

logger = logging.getLogger(__name__)


def bind_modports(component: Component) -> Component:
    """
    Bind the modport details to the original elements. This add a lot of information to the rendered page !
    """

    # First, is there anything to do ?
    if len(component.modports) == 0:
        return component

    # Build the signal registry:
    signals: dict[str, Signal] = dict([(x.name, x) for x in component.signals])

    # Now, iterate over each signals within the modports and bind the properties
    count = 0
    for modport in component.modports:
        for signal in modport.signals:

            # Fetch the target element
            target = signals.get(signal.name)
            if target is None:
                continue

            # Copy the hardware properties
            signal.hdl_type = target.hdl_type
            signal.hdl_size = target.hdl_size
            signal.hdl_sync = target.hdl_sync
            signal.hdl_reset = target.hdl_reset
            signal.hdl_value = target.hdl_value
            signal.hdl_polarity = target.hdl_polarity

            # Copy description (signals aren't rendered as an interface)
            signal.description = target.description

            # Copy the group and pair
            signal.group = target.group
            signal.pair = target.pair

            # Increment our counter
            count += 1

    count = 0

    if count > 0:
        logger.info(
            blue(
                f"[INFO] Bound {count} assignment{"s" if count > 1 else ""} to modport elements."
            )
        )

    return component
