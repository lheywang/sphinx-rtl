# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    20/10/2026
#
# Brief :   Define some utils used within the VHDL transformers
# ----------------------------------------------------------------------------

# Imports
from .size_type import get_size_type
from .vector import get_vector

# Define locally this variable
VHDL_KEYWORDS_AND_TYPES = {
    "std_logic",
    "std_logic_vector",
    "std_ulogic",
    "std_ulogic_vector",
    "unsigned",
    "signed",
    "integer",
    "boolean",
    "natural",
    "positive",
    "to",
    "downto",
    "and",
    "or",
    "not",
    "xor",
    "nand",
    "nor",
    "mod",
    "rem",
    "abs",
    "others",
    "null",
    "open",
    "true",
    "false",
}
