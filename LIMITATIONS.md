# Limitations

This file list the known limitations of each language at the date of the latest commit.

## SystemVerilog :

- Case generate aren't handled. (Modules will be shown, but without any badges specific to the construct).
- .\* are ignored for the ports connections of modules.
- modules counting does a (very) simple parsing of the text, therefore a loop (i = 0; i < 8; i += 2) would infer 8 instances.
- two modports cannot be defined on a single line.
- UVM is out of scope, and is therefore not matched on the line.
- tasks IO aren't seen.

# Cocotb

- Rendered elements are using the same workflow as the generic tool, but in a limited version. Only some elements relevant to the context are parsed :
  - Imports
  - Parameters (global variables in the file according to the PEP spec (uppercase))
  - Process (functions decorated with @cocotb.test())
