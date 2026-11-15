# test_dummy_alu.py
import cocotb  # type: ignore
from cocotb.triggers import Timer  # type: ignore


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

    assert dut.out.value == 15, f"Expected 15, got {dut.out.value}"
