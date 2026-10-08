# Contributing

Hello all !

This project is essentially a student project, there isn't any big ambitions behind it. Anyway, any ideas are welcomed, and may be merged into the
repository.

## How I'll work ?

I essentially work on my side, with little to no interactions with the other. A common TO-DO list will be done, and users may attribute themselves a task.

## To do

This is essentially my own list, but this could be extended to anyone ! Grab a free task, and here we go !

### Languages support

- [ ] Spinal HDL (Target > v1.0.0) --> Usage of a standard Scala plugin that dump a JSON object to be parsed.
- [ ] Chisel HDL (Target > v1.0.0) --> Usage of a standard Scala plugin that dump a JSON object to be parsed.
- [ ] SystemC (Target > v1.0.0) --> Usage of a standard Scala plugin that dump a JSON object to be parsed.
- [ ] Cocotb (Target < v1.0.0)
- [ ] VHDL (Target < v1.0.0)

### Features

- [ ] Make the render a bit cleaner (I don't know what, but things could get a bit better).
- [x] Add links between the elements, outside of the simple container. --> RTLDomain to be added
- [ ] Select the function rendering method (natural or complete).
- [ ] Add the register map inferring process + generation of the C compatible header file (and rust ?).
- [ ] Add the configuration layers models (sphinx-rtl.toml then arguments passed to the config then the flags on the file).
- [ ] CLI tool with different features
  - get include files for SystemC / Scala based and so
  - get output json from IR pass

### Tests and debug

- [ ] Test other edge-cases and bad documents.
- [ ] Ensure all elements are properly rendered.

### Examples

- [ ] Make the examples cleaner (more files, more text --> Better demonstration)
- [ ] Add a github workflow to push the rendered documentation to an example site
- [ ] Add the online site into the readme.md file

### Bugs to remove

- [ ] Incorrect size parsing (VariableSymbolDimension string is present.)
- [ ] Some structures are incorporating comments into the type. To be checked.
- [ ] SystemVerilog interfaces aren't correctly parsed --> Return an empty component.
- [ ] Grouping something use the second or third terms rather than the first. This lead to incorrect grouping methods.
