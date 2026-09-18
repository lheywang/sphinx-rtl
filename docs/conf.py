# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Library configuration file
# ----------------------------------------------------------------------------

# Imports
import sys
from pathlib import Path

# Ensure the code will be found
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Define basic settings
project = "Sphinx-RTL Test"
author = "Leonard HEYWANG"
release = "0.1.0"

# Ensure extensions
extensions = ["sphinx-rtl"]

# Configure sphinx
html_theme = "alabaster"
