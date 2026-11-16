Verilog
=================

Structure
----------------------
The repo in VHDL is structured around different folders, each for a dedicated section.

.. toctree::
    :maxdepth: 4

    clocks/clocks
    core/core
    memory/memory
    peripherals/peripherals
    
Top level 
----------------------

The top level file on VHDL isn't even finished, 
as this version did never pass the timing expectations of the project.


.. rtl-autodoc:: ../sources/verilog/rtl/rv32.sv
    :sim: Verilator 5.0.46