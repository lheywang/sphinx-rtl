# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

from .assignment import build_assignment
from .enum import build_enum
from .interface import build_interface
from .module import build_module
from .parameter import build_parameter
from .port import build_interfacePort, build_port
from .process import build_process
from .signal import build_signal
