Example of RTL documentation
=============================

Welcome on the documentation ! Here some examples.

Models of imports :
--------------------

.. rtl-autodoc:: ../examples/vhdl/*.vhd
    :sim: GHDL 5.1.1
    :license: MIT License
    :deprecated: VHDL version is no more supported. Use the SystemVerilog version.
    :notemplate:

.. rtl-autodoc:: ../examples/systemverilog/*.sv
    :sim: Verilator 5.046
    :license: Apache 2.0
    :nosource:

