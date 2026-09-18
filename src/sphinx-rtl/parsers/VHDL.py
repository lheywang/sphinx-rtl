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

# Logger config
logger = logging.getLogger(__name__)


class VHDLParser:
    """
    Define the standard Verilog Parser model.
    Designed to be reused (can be openned only once and parse more than one file).
    """

    def __init__(self):
        """
        Init the xVerilog parser for different operations.
        """

        # Ensure the tools are presents
        self.isGHDLAvailable = False
        self.cmd = shutil.which("ghdl")
        if self.cmd is not None:
            logger.info(f"Found GHDL at {self.cmd}")
            self.isGHDLAvailable = True
        else:
            logger.error("Cannot found a valid GHDL install.")

    def parse_file(self, file: Path):
        """
        Parse the passed file as VHDL, and output the built class.
        """
        pass
