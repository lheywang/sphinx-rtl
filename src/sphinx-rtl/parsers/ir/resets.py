# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Resolve the resets that interract in Writes for
#           a port / signal
# ----------------------------------------------------------------------------

# Imports
from ...models import Component, Port, Signal
import itertools

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_resets(component: Component) -> Component:
    """
    Infer the resets for a port or signal.
    """

    # Fetch the ports names :
    names = dict(
        [
            (x.name, x)
            for x in itertools.chain(component.signals, component.ports)
            if ((x.direction == "output") and type(x) is Port) or (type(x) is Signal)
        ]
    )

    # Iterate over the process (the only that could have a sync !)
    count = 0
    for process in component.process:
        for target in itertools.chain(process.signals, process.signals_write):
            obj = names.get(target, None)
            if obj is not None:
                setattr(obj, "hdl_reset", process.hdl_reset)
                count += 1

    if count > 0:
        logger.info(
            f"[INFO] Attached resets to {count} port{"s" if count > 1 else ""} and signal{"s" if count > 1 else ""}."
        )

    return component
