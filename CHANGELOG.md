# Changelogs

The changelogs are tied to git tags.
Each version is available on git, except when specified.

## [v0.1.0]

_Note : This version is not available under a git tag_

- Initial commit for most of the files.
- PyPi name reservation.

## [v0.2.0]

_Note : This version is not available under a git tag_

- Finished the base models for all the structures
- Finished the xVerilog support.

## [v0.3.0] / [v0.3.1]

- Finished the IR inferring engine, to extract more data than the AST could say.
- Updated models for some structures.

## [v0.4.0] / v[0.4.1]

- Finished the first render engine.
- Updated models to be inherited from others to ensure properties are presents in important places. This especially target the signals.
- Forgot to update the PyPi version. Updated it into v0.4.1. The later one was the only being pushed to the PyPi.

## [v0.4.2]

- Patched different bugs (modport support in ports, comments that where leaking ...)
- Refactored the grouping system to be more robust, and cleaner when rendered !

## [v0.5.0]

- Changed the project structure to exploit the sphinx BuildEnvironment feature. This enable higher quality builds (faster due to the cache,
  more analysis possibles as the elements are analyzed after parsing all of them ...).
