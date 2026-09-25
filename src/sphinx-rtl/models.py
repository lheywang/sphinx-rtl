# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the standard interface between the different parsers for the
#           different supported languages.
# ----------------------------------------------------------------------------

from dataclasses import dataclass, field


@dataclass
class Element:
    """
    Basic config for an element to be defined. Shall not be used as it.
    This ensure that Python will always find these elements in all class, regardless of the type.

    Fields :
        - name :            Store the name of the element.
        - description :     Store the description of the element, typically the comment that is known to be attached for.
        - line :            The line where the definition was found.
    """

    name: str = ""
    description: str = ""
    line: int = -1


@dataclass
class Parameter(Element):
    """
    Store the different values for a single parameter (or generic in VHDL) entry.

    Fields :
        - hdl_type :        The type of the Parameter.
        - hdl_value :       The default value of the parameter (may also be the assigned value if called from a Module class)
    """

    hdl_type: str = ""
    hdl_value: str = ""


@dataclass
class Port(Element):
    """
    Store the different values for a single port entry.

    Fields :
        - direction :       The direction of the port (input, output, inout...)
        - hdl_type :        The type of the port, as passed on the file. May be standard or custom ports.
        - hdl_size :        An array of N pairs of size, typically MSB:LSB. Single bit ports are expressed as "0", "0" (or any same value pair)
        - hdl_sync :        The clock to which this port is linked, in both reading and writing. This is inferred by the IR reduction pass.
        - hdl_reset :       The reset port to which this port is linked, in writing only.
    """

    direction: str = ""
    hdl_type: str = ""
    hdl_size: list[str] = field(default_factory=list)
    hdl_sync: str = ""
    hdl_reset: str = ""


@dataclass
class Enum(Element):
    """
    Store the different values for single enumeration (or type in VHDL) entry.

    Fields :
        - values :          The different elaboration resolved values for the enum.
        - members :         The different members to be available on the file for this enum.
    """

    values: list[int] = field(default_factory=list)
    members: list[str] = field(default_factory=list)


@dataclass
class Import(Element):
    """
    Store the different values for a single import (Verilog Only) entry.

    Fields :
        - library :         The name of the element to be imported.
        - element :         The name of the element to be imported within the provided library.
    """

    library: str = ""
    element: list[str] = field(default_factory=list)


@dataclass
class Signal(Element):
    """
    Store the different values for a single single reg / wire (or signal in VHDL) entry.

    Fields :
        hdl_type :          The type of the signal as wrote on the source file.
        hdl_size :          The size of the signal, passed as N pairs of strings, typically under the form MSB,LSB. Single bit signals are expressed "x", "x" (or any value, they just must be equal)
        hdl_value :         The value hold by this signal when declared.
    """

    hdl_type: str = ""
    hdl_size: list[str] = field(default_factory=list)
    hdl_value: str = ""


@dataclass
class Assignment(Element):
    """
    Store a constant assignment for a variable.

    Fields :
        - target :          The target signal name to be assigned.
        - source :          The list of the source signals to be involved into this assignment.
        - isComb :          Indicate that this assignment include more than a source, meaning the assignment require combinatorial logic. This will be evaluated for the output type.
    """

    target: str = ""
    source: list[str] = field(default_factory=list)
    isComb: bool = True


@dataclass
class Process(Element):
    """
    Store the different values for a single process / alway entry.

    Fields :
        - hdl_type :        The type of process, could be "comb" or "flipflop". This indicate the structure of the process for the IR.
        - signals_write :   The signals to be affected by the process in write mode.
        - signals :         The list of signals to be read by the process. Before the IR pass, this store all the keywords, they'll be passed to the reducer before being outputted.
        - hdl_clock :       The list of signals to be seen as clocks for this process.
        - hdl_reset :       The list of signals to be seen as resets for this process. They'll all include "rst" or "reset" in their name, in any place.
    """

    hdl_type: str = ""
    signals_write: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    hdl_clock: list[str] = field(default_factory=list)
    hdl_reset: list[str] = field(default_factory=list)


@dataclass
class Modport(Element):
    """
    Store a modport informations.
    This class could only be used in xVerilog parser.

    Fields :
        signals :           The list of ports objects to be defined within the selected modport.
    """

    signals: list[Port] = field(default_factory=list)


@dataclass
class Interface(Element):
    """
    Store the config for an interface entry.

    Fields :
        - parameters :      The list of passed parameters to the interface.
        - ports :           The list of ports of the interface.
        - signals :         The list of signals within the interface.
        - modports :        The list of modports for this inferace.
    """

    parameters: list[Parameter] = field(default_factory=list)
    ports: list[Port] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    modports: list[Modport] = field(default_factory=list)


@dataclass
class Module(Element):
    """
    Store the config for a known module, instantiated within the passed design.

    Fields :
        - entity :          The entity name of the included module.
        - connections :     A list of string tuples that match the port name and the actual connection name.
        - params :          The list of parameters passed to this module.
        - isVendor :        Does the module target something that looks like a vendor primitive ?
        - vendor :          The name of the vendor of this module, if applicable.
    """

    entity: str = ""
    connections: list[tuple[str, str]] = field(default_factory=list)
    params: list[Parameter] = field(default_factory=list)
    isVendor: bool = False
    vendor: str = ""


@dataclass
class FileInfo:
    """
    Store the different values for a single file info entry.
    Most of these fields are targeted by a git repo to be fetched, therefore it is the most complete within a repo.
    A fallback from the OS filesystem may be used.

    Fields :
        - name :            The name of the file
        - path :            The path of the file
        - creation_author : The name of the author which created the file, ie the name of the first committer for this file. This field remain unresolved when the FS fallback is used.
        - creation_hash :   The hash of the first commit which affected this file. This field remain unresolved when the FS fallback is used.
        - creation_date :   The date of the first commit which was affected by this file. This field remain unresolved when the FS fallback is used.
        - edit_author :     The name of the latest author which committed this file. This field is resolved to the current user logged when building the doc. Therefore may be wrong for CICD based systems.
        - edit_hash :       The hash of the latest commit which included this file. This field remain unresolved when the FS fallback is used.
        - edit_date :       The date of the latest commit which included this file. This field is resolved to the latest date known to the OS.
        - is_dirty :        Does this file contain changes that are not committed when building the doc ?
        - message :         The latest commit message.
    """

    name: str = ""
    path: str = ""
    creation_author: str = ""
    creation_hash: str = ""
    creation_date: str = ""
    edit_date: str = ""
    edit_hash: str = ""
    edit_author: str = ""
    is_dirty: bool = False
    message: str = ""


@dataclass
class ComponentConfig:
    """
    Store additional elements for the Component object, that are more
    linked to the user config rather than pure HDL elements.

    Fields :
        - isTestbench :     Define the current component as a testbench. This change some behaviors when the rendering pass is done.
        - testbenchTarget : The name of the component to be tested. Only evaluated if this module is a testbench.
        - status :          The status of the component. Could be any string, but standard (beta, release, stable ...) shall be preferred.
        - version :         The version of the module.
        - task :            Insert here the current task this module is relevant to. Could be @task Project XX or @task Client YY
        - copyright :       Is this module copyrighted to anything ?
        - tags :            A list of free tags to be used anywhere.
    """

    # @testbench
    isTestbench: bool = False

    # @target module_xx
    testbenchTarget: str = ""

    # @status released
    status: str = "release"

    # @version 1.0.0
    version: str = "1.0.0"

    # @task JIRA-928
    task: str = ""

    # @copyright Altera Corp.
    copyright: str = ""

    # @tags Done
    tags: list[str] = field(default_factory=list)


@dataclass
class Component:
    """
    Store all the infos for a component. Include all infos to be shared.

    Fields :
        - file :            The FileInfo class that store all elements.
        - name :            The name of the component to be used.
        - brief :           The brief description of the component.
        - details :         The long description of the component.
        - config :          The extended config file to be used.

        - parameters :      The list of available parameters for this component.
        - ports :           The list of module ports.
        - enums :           The list of module enums.
        - imports :         The list of imports for the module.
        - signals :         The list of internal signals.
        - process :         The list of internal process within the module.
        - assigns :         The list of internal assignments.
        - interfaces :      The list of available interfaces. Only exposed when this file describe at least an interface.
        - modules :         The list of included elements within the design.

        - flags :           The list of unresolved flags, to be passed to the render stage(s).
    """

    # File infos
    file: FileInfo

    # Basic infos
    name: str = ""
    brief: str = ""
    details: str = ""

    # Render config
    config: ComponentConfig = ComponentConfig()

    # HDL elements
    parameters: list[Parameter] = field(default_factory=list)
    ports: list[Port] = field(default_factory=list)
    enums: list[Enum] = field(default_factory=list)
    imports: list[Import] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    process: list[Process] = field(default_factory=list)
    assigns: list[Assignment] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)
    modules: list[Module] = field(default_factory=list)

    # Unknown flags
    flags: list[str] = field(default_factory=list)
