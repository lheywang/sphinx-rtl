# Contributing

Hello all !

This project is essentially a student project, there isn't any big ambitions behind it.
Anyway, any ideas are welcome and may be merged into the repository.

## How I'll work ?

I essentially work on my side, with little to no interactions with the other.
A common TO-DO list will be done, and users may attribute themselves a task.

## To do

This is essentially my own list, but this could be extended to anyone !
Grab a free task, open an issue or a PR, and here we go!

> It may be useful to submit a PR with your name / nickname on the task !

---

### Target 1.0.0

- [x] ~~Support Cocotb~~
- [x] ~~CLI tool with different features~~
  - ~~get output json from IR pass~~
- [x] ~~Select the function rendering method (natural or complete).~~ (Feature cancelled, useless for now)
- [x] ~~Add a FanIN / FanOUT inferring pass into the IR (and the matching flag to it !)~~
- [x] ~~Add a clock domain crossing detection feature.~~
- [x] ~~Correct a bug where the comments on multilines aren't properly rendered.~~
- [x] ~~Update the comment linking feature, as I think sometimes things aren't really matched as they should ? (to be verified before.)~~
- [x] ~~Add a github workflow to push the rendered documentation to an example site~~
- [x] ~~Add the online site into the readme.md file~~
- [x] ~~VHDL package / records must be handled~~
- [ ] VHDL package assignment shall not only use the last element on it. (WHAATT ???)
- [x] ~~VHDL : Bug : i variable from loop are used as assignment target --> Must be ignored.~~
- [x] ~~Make the render a bit cleaner (I don't know what, but things could get a bit better). Perhaps ask the community ?~~
  - ~~Add some better CSS to it.~~ (Let the users do it, won't perturb too much with their CSS.)
- [x] ~~Test other edge-cases and bad documents.~~
- [ ] Ensure all elements are properly rendered.
- [x] ~~Make the examples cleaner (more files, more text --> Better demonstration)~~
- [x] ~~Dropdown are not working great on dark mode.~~
- [ ] Some links on fallbacks are NOT correctly handled. Must be corrected.

---

_(Note: Feature requests for AXI/Avalon buses, IPact, HWtcl, SpinalHDL, ChiselHDL, and SystemC have been permanently_
_cancelled to keep Sphinx-RTL focused purely on low-level RTL. For bus-centric designs, please use PeakRDL instead.)_
