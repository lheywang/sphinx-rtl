Core
============================

Structure
----------------------------

This time, the core is much more organized for the reader.

.. toctree::
    :maxdepth: 4

    elements/alu
    elements/assemblies

Utilities
--------------------------

.. rtl-autodoc:: ../sources/verilog/rtl/core/clock.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/delay.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/reset.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/endianess.sv
    :sim: Verilator 5.0.46

Counters
--------------------------

.. rtl-autodoc:: ../sources/verilog/rtl/core/counter.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/pcounter.sv
    :sim: Verilator 5.0.46

Prediction & Decoder
--------------------------

.. rtl-autodoc:: ../sources/verilog/rtl/core/decoder.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/prediction.sv
    :sim: Verilator 5.0.46

Registers
--------------------------
.. rtl-autodoc:: ../sources/verilog/rtl/core/registers.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/csr.sv
    :sim: Verilator 5.0.46

ALU Managers
--------------------------

.. rtl-autodoc:: ../sources/verilog/rtl/core/issuer.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/commiter.sv
    :sim: Verilator 5.0.46

.. rtl-autodoc:: ../sources/verilog/rtl/core/occupancy.sv
    :sim: Verilator 5.0.46


ALU Managers
--------------------------

.. rtl-autodoc:: ../sources/verilog/rtl/core/core.sv
    :sim: Verilator 5.0.46


