# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the queries needed by the system.
# ----------------------------------------------------------------------------

# Imports
from .queries import get_queries
from .transformer_queries import (
    MODULE_CASE_Q,
    MODULE_IF_Q,
    MODULE_LOOP_Q,
    MODULE_PARAM_Q,
    MODULE_PORT_Q,
    ENUM_Q_MEMBERS,
    PORTS_ANSI_VARIABLE_Q,
    PORTS_ANSI_INTERFACE_Q,
    PORTS_ANSI_NET_Q,
    PORTS_NON_ANSI_INTERFACE_Q,
    PORTS_NON_ANSI_REF_Q,
    PORTS_NON_ANSI_INPUT_OUTPUT_Q,
    PORTS_NON_ANSI_INOUT_Q,
    PARAMS_ELEMENTS_Q,
)
