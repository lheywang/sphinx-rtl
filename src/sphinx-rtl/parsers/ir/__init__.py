# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Handle the properties management of the different modules,
#           under the name of the main parser.
# ----------------------------------------------------------------------------

from .assigns import infer_assigns
from .clocks import infer_clocks
from .groups import infer_groups
from .module_type import infer_type
from .polarity import infer_polarity
from .process import infer_process
from .resets import infer_resets
from .vendors import infer_vendors
