# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Expose the language API to be used.
# ----------------------------------------------------------------------------

# Imports
from .language import LanguageSpec, get_text

# Add other languages
from .vhdl import VHDLSpecification
from .systemverilog import SystemverilogSpecification
