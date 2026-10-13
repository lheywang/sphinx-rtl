# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Library configuration file
# ----------------------------------------------------------------------------

# Imports
import sys
from pathlib import Path
from sphinx_rtl.RTLConfig import RTLConfig

# Ensure the code will be found
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Define basic settings
project = "Sphinx-RTL Test"
author = "Leonard HEYWANG"
release = "0.1.0"

# Ensure extensions
extensions = ["sphinx_rtl"]

# Configure sphinx
html_theme = "alabaster"

html_theme_options = {
    "page_width": "1800px",
    "body_max_width": "auto",
    "sidebar_width": "280px",
}

# Configure the project
rtl_config = RTLConfig()
rtl_config.configure_shown_elements(mermaid=False, wavedrom=False)
rtl_config.configure_resolution(modules=True)
rtl_config.add_public_output("db.json")
rtl_config.add_public_output("backup/db_bckp.json")
rtl_config.add_private_output("db_nda.json")
rtl_config.add_component_source("../examples/db_nda.json")
