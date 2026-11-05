# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    04/11/2026
#
# Brief :   Import the generated samples code for the register map
# ----------------------------------------------------------------------------

# Imports
from .cpp import generate_c_header
from .rust import generate_rust_header
from .padder import compute_register_layout

# Define the supported instantiation languages
HEADER_LANGUAGES = ["C / C++", "Rust"]

HEADER_CALLBACKS = {
    "C / C++": generate_c_header,
    "Rust": generate_rust_header,
}

PYGMENTS_HEADER_LANG = {
    "C / C++": "c",
    "Rust": "rust",
}
