# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Import all the transformers
# ----------------------------------------------------------------------------

# Imports
from typing import Callable

from .comment import CocotbTransformerComment
from .imports import CocotbTransformerImport
from .parameter import CocotbTransformerParameter
from .process import CocotbTransformerProcess


# Define the functions to get the keys
def get_transformers() -> dict[str, Callable]:

    return {
        "Q_COMMENTS": CocotbTransformerComment,
        "Q_IMPORTS": CocotbTransformerImport,
        "Q_PARAMETERS": CocotbTransformerParameter,
        "Q_PROCESS": CocotbTransformerProcess,
    }
