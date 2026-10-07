# Contributing

Hello all !

This project is essentially a student project, there isn't any big ambitions behind it. Anyway, any ideas are welcomed, and may be merged into the
repository.

## How I'll work ?

I essentially work on my side, with little to no interactions with the other. A common TO-DO list will be done, and users may attribute themselves a task.

## To do :

### Languages support :

[ ] Spinal HDL
[ ] Chisel HDL
[ ] Cocotb
[ ] VHDL -> This is scheduled to be done before the 1.0.0 release.

### Features :

[ ] Make the render a bit cleaner
[ ] Add links between the elements, outside of the simple container. --> RTLDomain to be added
[ ] Select the function rendering method (natural or complete).

### Tests and debug :

[ ] Test other edge-cases and bad documents.
[ ] Ensure all elements are properly rendered.

### Bugs to remove

[ ] Incorrect size parsing (VariableSymbolDimension string is present.)
[ ] Some structures are incorporating comments into the type. To be checked.
[ ] SystemVerilog interfaces aren't correctly parsed --> Return an empty component.
[ ] Grouping something use the second or third terms rather than the first. This lead to incorrect grouping methods.
