# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    16/11/2026
#
# Brief :   Showcase configuration file
# ----------------------------------------------------------------------------

# Imports
import sys
from pathlib import Path
from sphinx_rtl.models import RTLConfig, ComponentConfig

# Ensure the code will be found
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Define basic settings
project = "Sphinx-RTL Test"
author = "Leonard HEYWANG"
release = "1.0.0"

# Ensure extensions
extensions = ["sphinx_rtl"]


html_theme_options = {
    "body_max_width": "auto",
}

# Configure the project
rtl_config = RTLConfig()
rtl_config.configure_shown_elements()
rtl_config.configure_resolution(modules=True)
# rtl_config.add_public_output("db.json")
# rtl_config.add_public_output("backup/db_bckp.json")
# rtl_config.add_private_output("db_nda.json")
# rtl_config.add_component_source("../examples/db_nda.json")

components = ComponentConfig()
components.set_legal(license="MIT License")

# Use the ReadTheDocs theme here
html_theme = "furo"
