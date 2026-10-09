# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    04/10/2026
#
# Brief :   Resolve the assigns signals, and perhaps the clocks and resets
#           associated to it.
# ----------------------------------------------------------------------------

# Imports
from ...models import Component
import itertools

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_assigns(component: Component) -> Component:
    """
    Infer the different assignments consequences (clocks, resets ...)
    """

    # First, fetch the elements
    port_names = dict([(x.name, x) for x in component.ports])
    signals_names = dict([(x.name, x) for x in component.signals])

    count = 0
    for assign in component.assigns:

        # Look only for the sync assignments. The comb ones aren't used, as they're the default print method on the doc ...
        if not assign.isComb:

            target = port_names.get(assign.target)
            if target is not None:

                # Now, search for the source
                for source in assign.source:
                    source_obj = port_names.get(source)
                    if source_obj is None:
                        source_obj = signals_names.get(source)

                    # If we did found something that would match, assign them.
                    # There could only be a single element, as the system CANNOT be combinatorial, which is triggered by the presence of more than 1 operand.
                    if source_obj is not None:

                        # Update element
                        target.hdl_sync = source_obj.hdl_sync
                        target.hdl_reset = source_obj.hdl_reset
                        count += 1

    if count > 0:
        logger.info(
            f"[INFO] Detected {count} assignment{"s" if count > 1 else ""} and updated the target settings to match the source settings."
        )

    return component
