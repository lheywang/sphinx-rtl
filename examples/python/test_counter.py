# Test the ALU operation modes.
# Multiples tests are done on this pass :
# - alu_reset : Ensures that the ALU will reset itself nicely
# - alu_addition : Did an operation completed successfully.
#
# @hascdc

import cocotb  # type: ignore
from cocotb.triggers import Timer  # type: ignore
import logging

# Define the timeout of all tests cases.
TIMEOUT_NS = 5000

# Define our logger
logger = logging.getLogger(__name__)


# Define a custom helper
def do_add(a, b):
    return a + b


@cocotb.test()
async def test_alu_reset(dut):
    """Test the reset behavior of the ALU module."""
    dut.rst.value = 1
    dut.a.value = 0
    dut.b.value = 0
    await Timer(20, units="ns")

    dut.rst.value = 0
    assert dut.out.value == 0, "Reset failed: output should be 0"


@cocotb.test()
async def test_alu_addition(dut):
    """Test basic addition operation on the ALU."""
    dut.rst.value = 0
    dut.a.value = 5
    dut.b.value = 10

    await Timer(20, units="ns")

    assert dut.out.value == do_add(
        dut.a.value, dut.b.value
    ), f"Expected 15, got {dut.out.value}"
