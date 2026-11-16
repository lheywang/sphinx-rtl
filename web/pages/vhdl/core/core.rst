Core
==========================

The core is the elements that is actually finished (I know, some may have doubted, if you've even read up to there !).
But, trust me, things will become nice !

Structure 
--------------------------
The core is composed of multiple elements, which are all defined here ! 

.. toctree::
    :maxdepth: 4

    elements/clock
    elements/controller
    elements/decoder
    elements/alu
    elements/registers
    elements/csr
    elements/counter
    elements/endianess

.. rtl-autodoc:: ../sources/vhdl/src/core/*.vhd
    :sim: GHDL 5.1.1
    :deprecated: VHDL version is no more supported. Use the SystemVerilog version.