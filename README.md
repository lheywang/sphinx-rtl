# sphinx-rtl 

A Python package to build docs for any RTL codes (VHDL, Verilog, SystemVerilog ...\*) and related programs (cocotb).
Operate in three steps : 
1. Extracting the data from the built AST and CST
2. Inferring elements by performing an analysis of the fetched nodes.
3. Render of the inferred elements into docutils nodes.
