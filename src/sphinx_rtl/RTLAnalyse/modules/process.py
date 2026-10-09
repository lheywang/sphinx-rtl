# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Fetch the process read and writes signals
# ----------------------------------------------------------------------------

# Imports
from ...models import Component

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_process(component: Component) -> Component:
    """
    Infer the signals the process use as inputs.
    """

    # First, fetch the list of inputs ports and the signals (which could be read and write)
    inputs = set([x.name for x in component.ports if x.direction in ["input", "inout"]])
    inputs |= set([x.name for x in component.signals])

    # Now, fetch the process inputs :
    for process in component.process:
        process_inputs = set(process.signals)
        process.signals = list(process_inputs & inputs)

    return component
