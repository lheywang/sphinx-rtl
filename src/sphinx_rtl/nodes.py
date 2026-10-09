# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    09/10/2026
#
# Brief :   Implement the most basic node, to act as a placeholder.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes


# Class
class RTLPlaceholderNode(nodes.General, nodes.Element):
    """
    Define a temp node to be placed right after the directive was executed.
    Won't exist in the final pass, as it's replaced by the RTLRender.
    """

    def __init__(self, name: str, base_doc: str) -> None:
        """
        Just store the most basic information. Won't be needed anyway ...
        """
        super().__init__()
        self["component_name"] = name
        self["base_doc"] = base_doc
