# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Resolve the resets that interract in Writes for
#           a port / signal
# ----------------------------------------------------------------------------

# Imports
from ...models import Component

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_resets(component: Component) -> Component:
    """
    Infer the resets for a port or signal.
    """
    return component
