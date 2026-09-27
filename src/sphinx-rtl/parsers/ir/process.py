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
    Infer the signals the process evaluate to.
    """
    return component
