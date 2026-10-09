# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Resolve the clocks that interract in both Read and Writes for
#           a port / signal
# ----------------------------------------------------------------------------

# Imports
from ...models import Component
import itertools

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_clocks(component: Component) -> Component:
    """
    Infer the clock of the different port and signals based on the process triggers lists.
    """

    # Fetch the port and signals names :
    names = dict(
        [(x.name, x) for x in itertools.chain(component.signals, component.ports)]
    )

    # Iterate over the process (the only that could have a sync !)
    count = 0
    clk_length = []
    for process in component.process:
        clk_length.append(len(process.hdl_clock))
        for target in itertools.chain(process.signals, process.signals_write):
            setattr(names[target], "hdl_sync", process.hdl_clock)
            count += 1

    # Add some logs
    clk_count = max(clk_length) if len(clk_length) > 0 else 0
    if count > 0:
        logger.info(
            f"[INFO] Attached {clk_count} clock{"s" if clk_count > 1 else ""} to {count} port{"s" if count > 1 else ""} and signal{"s" if count > 1 else ""}."
        )

    return component
