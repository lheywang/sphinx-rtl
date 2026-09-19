# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Build the standard VHDL parser.
#
# Require : GHDL
# ----------------------------------------------------------------------------

# Imports
import shutil
import logging
from pathlib import Path

from ..models import Component
from .xParser import xParser

# Logger config
logger = logging.getLogger(__name__)


class VHDLParser(xParser):
    """
    Define the standard VHDL Parser model.
    Designed to be reused (can be openned only once and parse more than one file).
    """

    def __init__(self):
        """
        Init the VHDL parser for different operations.
        """

        super().__init__("ghdl")

    def parse(self, file: Path):
        """
        Parse the passed file as VHDL, and output the built class.
        """
        pass
