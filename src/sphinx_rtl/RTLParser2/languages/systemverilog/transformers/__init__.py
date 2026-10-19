# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Import all the transformers
# ----------------------------------------------------------------------------

# Imports
from typing import Callable

from .ports import VHDLTransformerPort
from .signals import VHDLTransformerSignal


# Define the functions to get the keys
def get_transformers() -> dict[str, Callable]:

    return {
        "Q_PORTS": VHDLTransformerPort,
        "Q_SIGNALS": VHDLTransformerSignal,
    }
