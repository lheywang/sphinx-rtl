# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    15/11/2026
#
# Brief :   Define the queries used by the different parsers to dig
#           deeper in the AST.
# ----------------------------------------------------------------------------

# Imports
import tree_sitter_python

from tree_sitter import Language, Query

# As we use our own language, let's define it
VERILOG_LANGUAGE = Language(tree_sitter_python.language())
