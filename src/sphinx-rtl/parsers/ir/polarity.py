# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Infer the polarity of some signals.
# ----------------------------------------------------------------------------

# Imports
from ...models import Component

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_polarity(component: Component) -> Component:
    """
    Infer the polarity of the different port and signals based on the process triggers lists.

    Notes : Three options are possible at the end, for a simple reason of documentation clobbering.
    Therefore, only _p signals are flagged as positive, and _n signals are flagged as negatives.
    """
    return component
