# Limitations

This file list the known limitations of each language at the date of the latest commit.

## SystemVerilog :

- Case generate aren't handled. (Modules will be shown, but without any badges specific to the construct).
- .\* are ignored for the ports
- modules counting does a (very) simple parsing of the text, therefore a loop (i = 0; i < 8; i += 2) would infer 8 instances.

## VHDL

- Some elements are not parsed correctly, this shall be parsed on a later revision. Especially things that are based on regex and so on.
