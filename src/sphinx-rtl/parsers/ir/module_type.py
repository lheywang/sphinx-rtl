# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Infer the type of the module
# ----------------------------------------------------------------------------

# Imports
from ...models import Component

# Configure logger
from sphinx.util import logging

logger = logging.getLogger(__name__)


def infer_type(component: Component) -> Component:
    """
    Try to guess the module type.
    """
    return component
