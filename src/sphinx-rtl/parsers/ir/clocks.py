# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Resolve the clocks that interract in both Read and Writes for
#           a port / signal
# ----------------------------------------------------------------------------

# Imports
from ...models import Component

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_clocks(component: Component) -> Component:
    """
    Infer the clock of the different port and signals based on the process triggers lists.
    """
    return component
