Example of RTL documentation
=============================

Welcome on the documentation ! Here some examples.

Models of imports :
--------------------

.. rtl-autodoc:: ../examples/vhdl/*.vhd
    :tool: Quartus 25.1
    :sim: GHDL 5.1.1
    :target: Altera MAX10
    :notemplate:

.. rtl-autodoc:: ../examples/systemverilog/*.sv
    :tool: Quartus 25.1
    :sim: Verilator 5.046
    :target: Altera MAX10
    :nosource:

