VHDL
======================

Structure
----------------------
The repo in VHDL is structured around different folders, each for a dedicated section.

.. toctree::
    :maxdepth: 2

    packages/packages
    clocks/clocks
    core/core
    memory/memory
    peripherals/peripherals
    
Top level 
----------------------

The top level file on VHDL isn't even finished, 
as this version did never pass the timing expectations of the project.

.. rtl-autodoc:: ../sources/vhdl/src/rv32.vhd
    :sim: GHDL 5.1.1
    :deprecated: VHDL version is no more supported. Use the SystemVerilog version.
    :novendors: