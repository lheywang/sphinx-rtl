# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Assign transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node
from sphinx.util import logging

from sphinx_rtl.models import Component, FileInfo
from sphinx_rtl.RTLParser2.languages.utils import get_text

# Configure the logger
logger = logging.getLogger(__name__)


# Functions
def VHDLTransformerComponent(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Component | None:
    logger.error(
        "Attempted a call to VHDLTransformerComponent. This function DOES not return anything."
    )
    return None
