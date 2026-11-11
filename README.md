# Sphinx-RTL

A Python package to build docs for any RTL codes (VHDL, Verilog, SystemVerilog ...\*) and related programs (cocotb).
Operate in three steps :

1. Calling a file parser to build the AST, and naviguate within it. For [VHDL](https://github.com/jpt13653903/tree-sitter-vhdl), [SystemVerilog](https://github.com/tree-sitter/tree-sitter-verilog) and [CocoTB](https://github.com/tree-sitter/tree-sitter-python) files, this is done using [tree-sitter](https://github.com/tree-sitter/tree-sitter).
2. Inferring elements by performing an analysis of the fetched nodes.
3. Render of the inferred elements into docutils nodes.

It is designed to offer the lowest friction as possible for the user, by removing most of the documentation process. The code
says enough to be used !

## Summary

- [Sphinx-RTL](#sphinx-rtl)
  - [Summary](#summary)
  - [Scope](#scope)
  - [Main features](#main-features)
    - [RTLAnalyser](#rtlanalyser)
  - [How to use it ?](#how-to-use-it-)
    - [As an extension](#as-an-extension)
      - [Install the extension. It's available on PyPi, so :](#install-the-extension-its-available-on-pypi-so-)
      - [Add the extension to the project :](#add-the-extension-to-the-project-)
      - [Configure the used files :](#configure-the-used-files-)
      - [Configuring the extension](#configuring-the-extension)
      - [Connect events you may need](#connect-events-you-may-need)
      - [Run sphinx as you always did](#run-sphinx-as-you-always-did)
    - [As a CLI tool](#as-a-cli-tool)
      - [Configuration file](#configuration-file)
      - [Arguments](#arguments)
      - [Customizing the cleanup](#customizing-the-cleanup)
      - [Running the CLI](#running-the-cli)
  - [Advanced usages](#advanced-usages)
    - [Flags : A generic introduction](#flags--a-generic-introduction)
    - [Flags : A more precise description](#flags--a-more-precise-description)
    - [Flags : A complete list](#flags--a-complete-list)
      - [Component configuration](#component-configuration)
      - [Render configuration](#render-configuration)
  - [Plugin integration](#plugin-integration)
    - [Emitted events](#emitted-events)
  - [Author and License](#author-and-license)

## Scope

While Sphinx-RTL is designed for RTL, its main scope remains the "low level" RTL, where you want to see to which clocks a signal is tied, it's reset, the fan-out...
To ensures the best results, a scope was required. Therefore, buses (Avalon, AXI ...) are not identified as that; They remain for Sphinx-RTL simple signals with dedicated properties.

For this kind of works, I recommend using [PeakRDL](https://github.com/SystemRDL/PeakRDL) which would probably be more adapted to this task.

## Main features

What make Sphinx-RTL that nice ?

- **IR documentation pass** : Rather than purely parsing the file, we first read them all into our own IR, and then analyze it as a whole. Results are better !
- **Git integration** : The tool natively read your repo and search for commits, tags, author, messages ... No need to configure that in the top of the file. And it's by definition always up to date !
- **Plugin integration** : Add any custom Python code to edit on the fly the rendered page ! This enables NDA status, brands customizations or even CI/CD status network fetch !
- **Full support of Markdown for comments**. Feel free to add tables, images and more directly in the file. Any text provided by the user will go through Myst-parser !

An example of documentation built with it could be found here

![Example link](https://example.com)

### RTLAnalyser

The RTLAnalyzer module is composed of different options, almost all are optional.

| Name     | Action                                                                                                                    | Requirements                 |
| :------- | :------------------------------------------------------------------------------------------------------------------------ | :--------------------------- |
| io       | Infer the assignments for all sources (concurrent and process ones)                                                       | -                            |
| clocks   | Infer the clocks for all signals and ports                                                                                | io                           |
| resets   | Infer the resets for all signals and ports                                                                                | io                           |
| fanout   | Compute the fanout for all signals and ports.                                                                             | io                           |
| type     | Infer the type of modules (package, interface, testbench, or module (default))                                            | -                            |
| modules  | Fetch the properties of the module into the current module                                                                | (io for the fetched modules) |
| groups   | Identify signals groups (separator is `_`) and display them sorted on the web page. Especially useful for larger modules. | -                            |
| polarity | Identify signals polarity and add a marker to it.                                                                         | -                            |
| vendors  | Identify is a component depends on vendor primitives.                                                                     | -                            |

## How to use it ?

There are two ways of using Sphinx-RTL :

- [Sphinx](https://www.sphinx-doc.org/en/master/) extension, which will produce the standard output (HTML, Tex...)
- As a CLI tool, with the limited output to a .json file with all the analyzed components.

### As an extension

#### Install the extension. It's available on PyPi, so :

```sh
pip install sphinx-rtl
```

#### Add the extension to the project :

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

#### Configure the used files :

Add this line, configured as you need in the main `.rst` file.

```rst
.. rtl-autodoc:: ../examples/systemverilog/*.sv
.. rtl-autodoc:: ../examples/vhdl/*.vhd
    :sim: GHDL 5.1.1
    :license: MIT License
    :deprecated: VHDL version is no more supported. Use the SystemVerilog version.
    :notemplate:
```

> ℹ️ **INFO**
> The extension support to modes of adding files :
>
> - Glob (_, \*\*/_) and any valid syntax to the python glob module
> - specific files.
>
> To be noted : When the glob mode is used, all the modules found will be added to a single page, with all the elements.
> This can be especially useful for different but similar modules, but shall not be used as a primary documentation method.

> ℹ️ **INFO**
> The extension also enable some aliases :
>
> - vhdl-autodoc
> - sv-autodoc
>   They all do the same, without any differences.\*

#### Configuring the extension

This extension rely on the conf.py file used by sphinx for its own configuration to also fetch elements on it. For example, a
variable `rtl_config` of type `RTLConfig` (from `sphinx_rtl.models`) can be defined and used as a config !

```py
# Configure the project
rtl_config = RTLConfig()
rtl_config.configure_shown_elements()
rtl_config.configure_resolution(modules=True)
rtl_config.add_public_output("db.json")
rtl_config.add_public_output("backup/db_bckp.json")
rtl_config.add_private_output("db_nda.json")
rtl_config.add_component_source("../examples/db_nda.json")
```

This is enough to configure the whole builder !

#### Connect events you may need

The extension emit some events during its execution. It may be useful to connect them to your own callbacks.
Full details below ([Emitted events](#emitted-events)).

This feature is totally optional, the extension will work without and may not be needed at all !

#### Run sphinx as you always did

You may found a lot of documentation online, for example here the [command line reference](https://www.sphinx-doc.org/en/master/man/sphinx-build.html).
There may be a lot of others options, find the one that suit you !

### As a CLI tool

The CLI tool is based on runpy to get the config.
Forget long commands, you can just provide the configuration as a fixed file that will be executed !

The CLI tool is not designed to replace the global sphinx module, therefore only the analysis pass can be done.
The only output(s) JSON formatted ones.

#### Configuration file

The configuration file reuse most of the config from the sphinx extension, to remains coherent. The single extension done is the support for
another variable, `components` of type `ComponentConfig` (from `sphinx_rtl.models`).

```py
# Configure the project
rtl_config = RTLConfig()
rtl_config.configure_shown_elements()
rtl_config.configure_resolution(modules=True)
rtl_config.add_public_output("db.json")
rtl_config.add_public_output("backup/db_bckp.json")
rtl_config.add_private_output("db_nda.json")
rtl_config.add_component_source("../examples/db_nda.json")

# Let's also configure the components
components = ComponentConfig()
components.set_toolchain(
    "Altera MAX10", "Intel Quartus Prime Standard 24.1", "Verilator 5.0.55"
)
components.set_status("Active", "", "Issue #9999")
```

> ℹ️ **INFO**
> Unrecognized variables will be ignored for both modes.
>
> Therefore, a single config file may be used for all modes,
> making operations between the automated run and the command line unified.

#### Arguments

The CLI module support basic arguments. Configuration must be provided using the configuration file.

| Name        | Short | Type      | Description                                                                                                |
| :---------- | :---- | :-------- | :--------------------------------------------------------------------------------------------------------- |
| `--version` | `-v`  | boolean   | Print the version of the tool                                                                              |
| `--config`  | `-c`  | string    | Provide the configuration file path                                                                        |
| `--files`   | `-f`  | str [...] | Provide the file(s) to be analyzed by the tool                                                             |
| `--cleanup` | ---   | string    | Python function (or direct expression) for the cleanup. If not provided, the default function will be used |

#### Customizing the cleanup

One of the feature of the Sphinx extension is to provide an anchor for a custom cleanup of the database before JSON export.
This feature is also ported to the CLI package and could be defined as :

- (Recommended) A function name (defined in the configuration file !) to execute. The provided argument is a dict of type [str, Component].
- (Not recommended) A raw python expression.

The function will be called in between the two exports (standard and cleanup).

> ℹ️ **INFO**
> Due to the variation of processing, this feature couldn't be shared between sphinx extension and CLI.
> As a reminder, the sphinx extension does call this system through an event.

In the configuration file, this may looks like :

```py
# And why not defining a custom clean up function ?
def custom_cleanup(database):
    """
    Let's define a custom function, which is simpler than the default version
    """
    for component in database.values():

        # Clear internals
        component.signals.clear()
        component.modules.clear()

        # Reset file infos and parameters
        component.config = ComponentConfig()
        component.render = RTLConfig()
```

#### Running the CLI

The CLI can be invoked from anywhere in the system using its name.
It'll then produce an analyzed list of components under a JSON output.

For example

```sh
sphinx-rtl --files examples/systemverilog/*.sv examples/vhdl/*.vhd --config cli/config.py --cleanup "custom_cleanup(database)"
```

This will export as many JSON databases as specified in the configuration.

---

## Advanced usages

### Flags : A generic introduction

More advanced users may want to fine the output documentation. For this, sphinx-RTL propose a three level system :

| Method                                   | Scope                                |
| :--------------------------------------- | :----------------------------------- |
| conf.py (variables defined in the file). | All runs by the tool.                |
| Arguments passed to the directive.       | All files targeted by the directive. |
| Arguments added on the module.           | The file only.                       |

All the arguments are reusing an older syntax scheme, close to what Doxygen proposed. This look like :

```sh
@warning This module must be held in reset for at least 10 clock cycle.
```

Unless Doxygen, all of them are fully optional. Sphinx-RTL could perfectly run without any of them, and still
produce a decent option. The approach retained was
an additive process : You can only add element to the documentation to make it more precise. Flags affect two
different domains :

- The analyses done on the component, after all the parsing.
- The rendering of the component into nodes tree.

Some flags may disable the presence of certain elements in the final support.

### Flags : A more precise description

All the flags are defined in the documentation right below. For all of them, you'll find a description of it, how to use it,
and where it is available. Some does not make any sense at the top level, and are therefore excluded from the configuration.

A merging method is also defined, this is the logic used to define how a merge when going a level under is done.
Four method are used, depending on the flag itself.

- `append` : The parameter is added to the list already defined.
- `override` : The parameter replaces the old one.
- `logic or` : The parameter is the logic OR of both. Used for boolean.
- `logic and` : The parameter is the logic AND of both. Used for boolean where privacy can only be made more strict.

### Flags : A complete list

The flags are separated into two different groups :

- Component configuration : These flags add information to the component which could not be inferred from the RTLAnalyse pass.
- Render configuration : These flags add parameter on how to render the provided component.

All of these structures follow the life-cycle of the component, from its creation to the export.
An imported component will therefore use its creation configuration rather than the current one.

#### Component configuration

| Flag            | Syntax                                           | Description                                                                                            |   Global Config    |  Directive Config  |    File Config     | Override Method |
| :-------------- | :----------------------------------------------- | :----------------------------------------------------------------------------------------------------- | :----------------: | :----------------: | :----------------: | --------------- |
| warning         | `@warning <str>`                                 | Display a custom warning in top of the documentation.                                                  |        :x:         | :white_check_mark: | :white_check_mark: | `append`        |
| note            | `@note <str>`                                    | Display a custom note in top of the documentation.                                                     |        :x:         | :white_check_mark: | :white_check_mark: | `append`        |
| testbench       | `@testbench`                                     | Flag this module as a testbench.                                                                       |        :x:         |        :x:         | :white_check_mark: | `logic or`      |
| testbenchTarget | `@testbenchtarget`                               | Define the target of the testbench, i.e. the DUT.                                                      |        :x:         |        :x:         | :white_check_mark: | `override`      |
| package         | `@package`                                       | Flag this module as a package.                                                                         |        :x:         |        :x:         | :white_check_mark: | `logic or`      |
| interface       | `@interface`                                     | Flag this module as an interface.                                                                      |        :x:         |        :x:         | :white_check_mark: | `logic or`      |
| constraint      | `@constraint`                                    | Add a constraint for this module. Will be displayed in a nice code block.                              |        :x:         |        :x:         | :white_check_mark: | `append`        |
| clock           | `@clock <name> <frequency> <net>`                | Configure the clock speed for a net. Will be shown in the panel properties.                            |        :x:         |        :x:         | :white_check_mark: | `append`        |
| latency         | `@latency <cycles>`                              | Configure the module latency between input to output.                                                  |        :x:         |        :x:         | :white_check_mark: | `override`      |
| throughput      | `@throughput <str>`                              | Configure the throughput of the module.                                                                |        :x:         |        :x:         | :white_check_mark: | `override`      |
| register        | `@register <name> <offset> <size> <description>` | Add a register to the module, to support for memory mapped elements. A register map will be generated. |        :x:         |        :x:         | :white_check_mark: | `append`        |
| target          | `@target <name>`                                 | Configure the target (chip, node ...). Only used for indication.                                       | :white_check_mark: | :white_check_mark: | :white_check_mark: | `append`        |
| tool            | `@tool <name>`                                   | Configure the tool used. Only used for indication.                                                     | :white_check_mark: | :white_check_mark: | :white_check_mark: | `append`        |
| sim             | `@sim <name>`                                    | Configure the simulator used. Only used for indication.                                                | :white_check_mark: | :white_check_mark: | :white_check_mark: | `append`        |
| compliance      | `@compliance <name>`                             | Set the compliance target of the module. Could be anything, generally standard buses (AXI ...).        | :white_check_mark: | :white_check_mark: | :white_check_mark: | `override`      |
| burst           | `@burst <size>`                                  | Set the burst capacity of the module, for the standard buses.                                          |        :x:         |        :x:         | :white_check_mark: | `override`      |
| security        | `@security <name>`                               | Set the security level of the module, if applicable.                                                   | :white_check_mark: | :white_check_mark: | :white_check_mark: | `override`      |
| status          | `@status <status>`                               | Display the status of the module (alpha, beta, release, stable ...)                                    | :white_check_mark: | :white_check_mark: | :white_check_mark: | `override`      |
| deprecated      | `@deprecated <message>`                          | Set the module as deprecated. A message can be added in top of it.                                     | :white_check_mark: | :white_check_mark: | :white_check_mark: | `override`      |
| version         | `@version <version>`                             | Set the module version. Only used for indication.                                                      |        :x:         | :white_check_mark: | :white_check_mark: | `override`      |
| task            | `@task <name>`                                   | Set a task name for the module. Could be a git issue or a JIRA sprint ...                              | :white_check_mark: | :white_check_mark: | :white_check_mark: | `override`      |
| license         | `@license <name>`                                | Set the license for the file.                                                                          | :white_check_mark: | :white_check_mark: | :white_check_mark: | `append`        |
| copyright       | `@copyright <name>`                              | Set the copyright for the file.                                                                        | :white_check_mark: | :white_check_mark: | :white_check_mark: | `override`      |
| tag             | `@tag <name>`                                    | Set a custom tag for the file. Feel free to use any of them.                                           |        :x:         | :white_check_mark: | :white_check_mark: | `append`        |

#### Render configuration

| Flag        | Syntax         | Description                                                       |   Global Config    |  Directive Config  |    File Config     | Override Method |
| :---------- | :------------- | :---------------------------------------------------------------- | :----------------: | :----------------: | :----------------: | --------------- |
| noclocks    | `@noclocks`    | Disable the clock inferring process for ports (Output and input). | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| noresets    | `@noresets`    | Disable the reset inferring process for ports (Output only).      | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| fanout      | `@nofanout`    | Disable the fanout computation                                    | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| noio        | `@noio`        | Disable the process IO inferring pass.                            | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| notype      | `@notype`      | Disable the file type inferring (testbench, package ...)          | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| nopolarity  | `@nopolarity`  | Disable the polarity inferring process                            | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| nogroups    | `@nogroups`    | Disable the port group inferring pass                             | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| modules     | `@nomodules`   | Disable the inter-modules resolution.                             | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| nosource    | `@nosource`    | Disable the source copy on the documentation.                     | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| notemplate  | `@notemplate`  | Disable the template instance generation.                         | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| nosignals   | `@nosignals`   | Disable the signal show at the end of the doc.                    | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| nointernals | `@nointernals` | Disable the process / enums for the doc.                          | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| novendors   | `@novendors`   | Disable the vendors inferring pass                                | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |
| vendor      | `@vendor`      | Set the vendor manually.                                          | :white_check_mark: | :white_check_mark: | :white_check_mark: | `logic and`     |

## Plugin integration

Sphinx-rtl does not handle plugin individually, it rather depends on the native Sphinx plugin management.
Therefore, natively the plugin emit events that you can fetch by writing your own Sphinx extension, and listen to them.

> ℹ️ **INFO**
> Sphinx-RTL provide a "user" field into each Component object, free for the user. This enables passing data between events and to the rendering pass
> without having to maintain a dict of elements.
>
> By default, this "user" field is simply ignored by any rendering pass.

### Emitted events

| Event                   | Name                         | Arguments                    | Description                                                                                                                               |
| :---------------------- | :--------------------------- | :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| Pre Analyse             | `rtl-pre-analysis`           | app, env, components         | Provide the raw parsed components access before performing the analysis. For example to add infos that could not be fetched from the AST. |
| Post Analyse            | `rtl-post-analysis`          | app, env, components         | Provide the component after performing the analysis. For example to add infos or build a post analysis custom CI/CD format.               |
| FileInfo Rendering      | `rtl-card-rendered`          | app, env, context, component | Provide the access to the component card element to add a section between the description and the file information (git, edit ...).       |
| Component pre Render    | `rtl-pre-elements-rendered`  | app, env, context, component | Provide access to the first section of the component, before the parameters to be rendered.                                               |
| Component post Render   | `rtl-post-elements-rendered` | app, env, context, component | Provide access to the last section of the component.                                                                                      |
| Component clear request | `rtl-pre-private-export`     | app, env, components         | Request for the cleaning of the components. Must return the components as a list, otherwise the default function will be called.          |

## Author and License

This project is open-source software released under the [Apache 2.0 License](LICENSE).
That mean you can :

- Use, including commercially this tool to anyone.
- Distribute, in both source and binaries, including commercially this tool to anyone.

The conditions are :

- Attribute to owner of the project the copyrights,
- Give a copy of the license with any distribution,
- Notify the modifications done to the source code.

**Note** : Any documentation you've built is yours. These license statement does not apply to these.

> Developed by [**L. Heywang**](https://github.com/lheywang) <[l.heywang@proton.me](mailto:l.heywang@proton.me)> (2026).
