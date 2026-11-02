# Limitations

This file list the known limitations of each language at the date of the latest commit.

## SystemVerilog :

- Case generate aren't handled. (Modules will be shown, but without any badges specific to the construct).
- .\* are ignored for the ports connections of modules.
- modules counting does a (very) simple parsing of the text, therefore a loop (i = 0; i < 8; i += 2) would infer 8 instances.
- two modports cannot be defined on a single line.
- UVM is out of scope, and is therefore not matched on the line.
- tasks IO aren't seen.

## VHDL

- Some elements are not parsed correctly, this shall be parsed on a later revision. Especially things that are based on regex and so on.
