# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Import all the transformers
# ----------------------------------------------------------------------------

# Imports
from typing import Callable

from .assignment import VerilogTransformerAssignment
from .comment import VerilogTransformerComment
from .enum import VerilogTransformerEnum
from .imports import VerilogTransformerImport
from .interface import VerilogTransformerInterface
from .modport import VerilogTransformerModport
from .module import VerilogTransformerModule
from .parameter import VerilogTransformerParameter
from .port import VerilogTransformerPort
from .process import VerilogTransformerProcess
from .routine import VerilogTransformerRoutine
from .signal import VerilogTransformerSignal


# Define the functions to get the keys
def get_transformers() -> dict[str, Callable]:

    return {
        "Q_ASSIGNS": VerilogTransformerAssignment,
        "Q_COMMENTS": VerilogTransformerComment,
        "Q_ENUM": VerilogTransformerEnum,
        "Q_IMPORTS": VerilogTransformerImport,
        "Q_INTERFACES": VerilogTransformerInterface,
        "Q_MODPORTS": VerilogTransformerModport,
        "Q_MODULES": VerilogTransformerModule,
        "Q_PARAMETERS": VerilogTransformerParameter,
        "Q_PORTS": VerilogTransformerPort,
        "Q_PROCESS": VerilogTransformerProcess,
        "Q_FUNCTIONS": VerilogTransformerRoutine,
        "Q_SIGNALS": VerilogTransformerSignal,
    }
