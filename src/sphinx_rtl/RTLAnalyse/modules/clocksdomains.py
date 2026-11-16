# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Resolve the clocks that interract in both Read and Writes for
#           a port / signal
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import Component
import itertools

# Configure logger
from sphinx.util import logging
from sphinx._cli.util.colour import blue

logger = logging.getLogger(__name__)


def infer_clocksdomains(component: Component) -> Component:
    """
    Detect is there's more than one clock on the component ?
    """

    # Fetch the port and signals names :
    names = dict(
        [(x.name, x) for x in itertools.chain(component.signals, component.ports)]
    )

    # For any signals, is there more than one clock designated ?
    clocks: list[str] = []
    for item in names.values():
        if item.hdl_sync not in clocks:
            clocks.extend(item.hdl_sync)

    # Remove empty elements and duplicates
    clocks = list(set(clocks))
    clocks = [x for x in clocks if x]

    # If there are more than one clock in it, there are a CDC !
    if len(clocks) > 1:
        component.config.hasCDC = True
    else:
        component.config.hasCDC = False

    return component
