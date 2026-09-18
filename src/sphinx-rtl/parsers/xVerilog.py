# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Build the standard xVerilog (Verilog / SystemVerilog) parser.
# ----------------------------------------------------------------------------

# Imports
import shutil
import logging
from pathlib import Path

from ..models import Component

# Logger config
logger = logging.getLogger(__name__)


class xVerilogParser:
    """
    Define the standard Verilog Parser model.
    Designed to be reused (can be openned only once and parse more than one file).
    """

    def __init__(self):
        """
        Init the xVerilog parser for different operations.
        """

        # Ensure the tools are presents
        self.isVeribleAvailable = False
        self.cmd = shutil.which("verible-verilog-syntax")
        if self.cmd is not None:
            logger.info(f"Found verible at {self.cmd}")
            self.isVeribleAvailable = True
        else:
            logger.error("Cannot found a valid verible install.")

    def parse_file(self, file: Path):
        """
        Parse the passed file as verilog, and output the built class.
        """
        pass
