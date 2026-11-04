# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    03/11/2026
#
# Brief :   Define the different instances for the examples in the languages.
# ----------------------------------------------------------------------------

# Imports
from .verilog import instantiate_verilog
from .vhdl import instantiate_vhdl

# Define the supported instantiation languages
INSTANCE_LANGUAGES = ["Verilog / SystemVerilog", "VHDL"]

INSTANCE_CALLBACKS = {
    "Verilog / SystemVerilog": instantiate_verilog,
    "VHDL": instantiate_vhdl,
}

PYGMENTS_INSTANCE_LANG = {
    "Verilog / SystemVerilog": "systemVerilog",
    "VHDL": "vhdl",
}
