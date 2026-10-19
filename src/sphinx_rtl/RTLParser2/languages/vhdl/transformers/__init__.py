# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Import all the transformers
# ----------------------------------------------------------------------------

# Imports
from typing import Callable

from .assign import VHDLTransformerAssign
from .comments import VHDLTransformerComment
from .component import VHDLTransformerComponent
from .functions import VHDLTransformerFunction
from .generate import VHDLTransformerGenerate
from .imports import VHDLTransformerImport
from .modules import VHDLTransformerModule
from .parameter import VHDLTransformerParameter
from .ports import VHDLTransformerPort
from .process import VHDLTransformerProcess
from .signals import VHDLTransformerSignal
from .types import VHDLTransformerType


# Define the functions to get the keys
def get_transformers() -> dict[str, Callable]:

    return {
        "Q_COMMENTS": VHDLTransformerComment,
        "Q_IMPORTS": VHDLTransformerImport,
        "Q_PARAMETERS": VHDLTransformerParameter,
        "Q_PORTS": VHDLTransformerPort,
        "Q_SIGNALS": VHDLTransformerSignal,
        "Q_TYPES": VHDLTransformerType,
        "Q_PROCESSES": VHDLTransformerProcess,
        "Q_ASSIGNS": VHDLTransformerAssign,
        "Q_MODULES": VHDLTransformerModule,
        "Q_FUNCTIONS": VHDLTransformerFunction,
        "Q_GENERATE": VHDLTransformerGenerate,
        "Q_ENTITY": VHDLTransformerComponent,
    }
