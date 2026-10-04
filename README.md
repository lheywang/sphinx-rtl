# sphinx-rtl

A Python package to build docs for any RTL codes (VHDL, Verilog, SystemVerilog ...\*) and related programs (cocotb).
Operate in three steps :

1. Extracting the data from the built AST and CST
2. Inferring elements by performing an analysis of the fetched nodes.
3. Render of the inferred elements into docutils nodes.

It is designed to offer the lowest friction as possible for the user, by removing most of the documentation process. The code
says enough to be used !

## Main features

What make Sphinx-RTL better than others ? There are two points :

- IR documentation pass : By reading the intermediate representation after parsing the file, we can extract more information : Related clock, CDC, nets groups, outputs ...
- Git integration : The tool natively read your repo and search for commits, tags, author, messages ... No need to configure that in the top of the file.

An example could be found here

![Example link](https://example.com)

## How to use it ?

1. **Install the extension. It's available on PyPi, so :**

```sh
pip install sphinx-rtl
```

2. **Add the extension to the project :**

Add this line in the conf.py file you used for your sphinx documentation.

```py
extensions = ["sphinx-rtl"]
```

Even if the extension does support any width of prints via the support of lateral scrollbar, It's recommended to add these lines to your conf.py file

```py
html_theme_options = {
    "page_width": "1800px",
    "body_max_width": "auto",
    "sidebar_width": "280px",
}
```

This will make the reading wider, fitting the tables used with a cleaner aspect.

3. **Configure the used files :**

Add this line, configured as you need in the main rst file.

```rst
.. rtl-autodoc:: ../examples/systemverilog/*.sv
.. rtl-autodoc:: ../examples/vhdl/*.vhd
```

```
The extension support to modes of adding files :
- glob (*, **/*) and any valid syntax to the python glob module
- specific files.

To be noted : When the glob mode is used, all the modules found will be added to a single page, with all the elements.
This can be especially useful for different but similar modules, but shall not be used as a primary documentation method.
```

```
The extension also enable some aliases :

- vhdl-autodoc
- sv-autodoc
They all do the same, without any differences.*
```

4. **Run sphinx as you always did**

## Advanced usages

More advanced users may want to fine the output documentation. For this, sphinx-rtl propose a three level system :

| Method                                  | Scope                                |
| :-------------------------------------- | :----------------------------------- |
| config.toml at the root of the project. | All runs by the tool.                |
| arguments passed to the file.           | All files targeted by the directive. |
| arguments added on the module.          | The file only.                       |

All the arguments are reusing an older syntax scheme, close to what Doxygen proposed. This look like :

```
@warning This module must be held in reset for at least 10 clock cycle.
```

But, unless Doxygen, all of them are fully optional. Sphinx-RTL could perfectly run without any of them, and still produce a decent option. The approach retained was
an additive process : You can only add element to the documentation.

#### List of the flags :

| Flag       | Syntax                                           | Description                                                                                            |
| :--------- | :----------------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| warning    | `@warning <str>`                                 | Display a custom warning in top of the documentation.                                                  |
| notes      | `@notes <str>`                                   | Display a custom note in top of the documentation.                                                     |
| testbench  | `@testbench`                                     | Flag this module as a testbench.                                                                       |
| package    | `@package`                                       | Flag this module as a package.                                                                         |
| nterface   | `@interface`                                     | Flag this module as an interface.                                                                      |
| constraint | `@constraint`                                    | Add a constraint for this module. Will be displayed in a nice code block.                              |
| clock      | `@clock <name> <frequency> <net>`                | Configure the clock speed for a net. Will be shown in the panel properties.                            |
| latency    | `@latency <cycles>`                              | Configure the module latency between input to output.                                                  |
| throughput | `@throughput <str>`                              | Configure the throughput of the module.                                                                |
| register   | `@register <name> <offset> <size> <description>` | Add a register to the module, to support for memory mapped elements. A register map will be generated. |
| target     | `@target <name>`                                 | Configure the target (chip, node ...). Only used for indication.                                       |
| tool       | `@tool <name>`                                   | Configure the tool used. Only used for indication.                                                     |
| sim        | `@sim <name>`                                    | Configure the simulator used. Only used for indication.                                                |
| compliance | `@compliance <name>`                             | Set the compliance target of the module. Could be anything, generally standard buses (AXI ...).        |
| burst      | `@burst <size>`                                  | Set the burst capacity of the module, for the standard buses.                                          |
| security   | `@security <name>`                               | Set the security level of the module, if applicable.                                                   |
| status     | `@status <status>`                               | Display the status of the module (alpha, beta, release, stable ...)                                    |
| deprecated | `@deprecated <message>`                          | Set the module as deprecated. A message can be added in top of it.                                     |
| version    | `@version <version>`                             | Set the module version. Only used for indication.                                                      |
| task       | `@task <name>`                                   | Set a task name for the module. Could be a git issue or a JIRA sprint ...                              |
| license    | `@license <name>`                                | Set the license for the file.                                                                          |
| copyright  | `@copyright <name>`                              | Set the copyright for the file.                                                                        |
| tag        | `@tag <name>`                                    | Set a custom tag for the file. Feel free to use any of them.                                           |

### Configuration flags

These flags target the user, by enabling or disabling features for the final render.

```
@warning This module must be held in reset for at least 10 clock cycle.
```

#### List of the flags :

| Flag        | Syntax         | Description                                                                                              |
| :---------- | :------------- | :------------------------------------------------------------------------------------------------------- |
| noclocks    | `@noclocks`    | Disable the clock inferring process for ports (Output and input).                                        |
| noresets    | `@noresets`    | Disable the reset inferring process for ports (Output only).                                             |
| noio        | `@noio`        | Disable the process IO inferring pass.                                                                   |
| notype      | `@notype`      | Disable the file type inferring (testbench, package ...)                                                 |
| nopolarity  | `@nopolarity`  | Disable the polarity inferring process                                                                   |
| nogroups    | `@nogroups`    | Disable the port group inferring pass                                                                    |
| nosource    | `@nosource`    | Disable the source copy on the documentation.                                                            |
| nomermaid   | `@nomermaid`   | Disable the mermaid package from a CDN. Could be required for portable doc without internet connection.  |
| wavedrom    | `@wavedrom`    | Disable the wavedrom package from a CDN. Could be required for portable doc without internet connection. |
| notemplate  | `@notemplate`  | Disable the template instance generation.                                                                |
| nosignals   | `@nosignals`   | Disable the signal show at the end of the doc.                                                           |
| nointernals | `@nointernals` | Disable the process / enums for the doc.                                                                 |
| novendors   | `@novendors`   | Disable the vendors inferring pass                                                                       |
| vendor      | `@vendor`      | Set the vendor manually.                                                                                 |
