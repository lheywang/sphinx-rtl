# Contributing

Hello all !

This project is essentially a student project, there isn't any big ambitions behind it. Anyway, any ideas are welcomed, and may be merged into the
repository.

## How I'll work ?

I essentially work on my side, with little to no interactions with the other. A common TO-DO list will be done, and users may attribute themselves a task.

## To do

This is essentially my own list, but this could be extended to anyone ! Grab a free task, and here we go !

### Target v0.6.0

- [ ] VHDL (Target < v1.0.0)
- [ ] Add the flag processing method
- [ ] Add the configuration layers models (~~sphinx-rtl.toml~~ (replaced by the RTLConfig helpers) then arguments passed to the config then the flags on the file).
- [ ] Migrate the Verilog parser to tree-sitter based one. Faster and unify both processing lines (more reliable, easier to maintain).

### Target v0.7.0

- [ ] Make the render a bit cleaner (I don't know what, but things could get a bit better). Perhaps ask the community ?
- [ ] CLI tool with different features
  - get include files for SystemC / Scala based and so
  - get output json from IR pass
- [ ] Add the snipplet generator into the renderer engine.
- [ ] Select the function rendering method (natural or complete).
- [ ] Add the register map inferring process + generation of the C compatible header file (and rust ?).

### Target v0.8.0+

- [ ] Cocotb (Target < v1.0.0)
- [ ] IPact (Target < v1.0.0)
- [ ] HWtcl (Target < v1.0.0) --> Emulate the TCL shell by mocking up the functions
- [ ] Spinal HDL (Target > v1.0.0) --> Usage of a standard Scala plugin that dump a JSON object to be parsed.
- [ ] Chisel HDL (Target > v1.0.0) --> Usage of a standard Scala plugin that dump a JSON object to be parsed.
- [ ] SystemC (Target > v1.0.0) --> Usage of a standard Scala plugin that dump a JSON object to be parsed.
- [ ] Test other edge-cases and bad documents.
- [ ] Ensure all elements are properly rendered.
- [ ] Make the examples cleaner (more files, more text --> Better demonstration)
- [ ] Add a github workflow to push the rendered documentation to an example site
- [ ] Add the online site into the readme.md file
