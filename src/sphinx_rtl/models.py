# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the standard interface between the different parsers for the
#           different supported languages.
# ----------------------------------------------------------------------------

from dataclasses import dataclass, field
from .RTLConfig import RTLConfig


@dataclass(slots=True)
class Element:
    """
    Basic config for an element to be defined. Shall not be used as it.
    This ensure that Python will always find these elements in all class, regardless of the type.

    Inherit from : None

    Fields :
        - name :            Store the name of the element.
        - description :     Store the description of the element, typically the comment that is known to be attached for.
        - line :            The line where the definition was found.
    """

    name: str = ""
    description: str = ""
    line: int = -1


@dataclass(slots=True)
class Parameter(Element):
    """
    Store the different values for a single parameter (or generic in VHDL) entry.

    Inherit from : Element

    Fields :
        - hdl_type :        The type of the Parameter.
        - hdl_value :       The default value of the parameter (may also be the assigned value if called from a Module class)
    """

    hdl_type: str = ""
    hdl_value: str = ""


@dataclass(slots=True)
class Port(Element):
    """
    Store the different values for a single port entry.

    Inherit from : Element

    Fields :
        - direction :       The direction of the port (input, output, inout...)
        - hdl_type :        The type of the port, as passed on the file. May be standard or custom ports.
        - hdl_size :        An array of N pairs of size, typically MSB:LSB. Single bit ports are expressed as "0", "0" (or any same value pair)
        - hdl_value :       The default value given for the port.
        - hdl_sync :        The clock to which this port is linked, in both reading and writing. This is inferred by the IR reduction pass.
        - hdl_reset :       The reset port to which this port is linked, in writing only.
        - hdl_polarity :    The level to which this port is sensible. Only inferred by the "name" on it...
        - group :           Inferred by the group selection.
        - pair :            Did we found some ports that can be matched in differential pairs ?
    """

    direction: str = ""
    hdl_type: str = ""
    hdl_size: list[str] = field(default_factory=list)
    hdl_value: str = ""
    hdl_sync: str = ""
    hdl_reset: str = ""
    hdl_polarity: str = ""
    group: str = ""
    pair: str = ""


@dataclass(slots=True)
class Enum(Element):
    """
    Store the different values for single enumeration (or type in VHDL) entry.

    Inherit from : Element

    Fields :
        - values :          The different elaboration resolved values for the enum.
        - members :         The different members to be available on the file for this enum.
    """

    values: list[int] = field(default_factory=list)
    members: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Structure(Element):
    """
    Store the element contained within a structure.

    Inherit from : Element

    Fields :
        - signals:          A list of signals to be stored within the struct.
        - isPacked :        Is the struct packed ?
    """

    signals: list[Signal] = field(default_factory=list)
    isPacked: bool = False


@dataclass(slots=True)
class Import(Element):
    """
    Store the different values for a single import (Verilog Only) entry.

    Inherit from : Element

    Fields :
        - library :         The name of the element to be imported.
        - element :         The name of the element to be imported within the provided library.
    """

    library: str = ""
    element: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Signal(Port):
    """
    Store the different values for a single single reg / wire (or signal in VHDL) entry.

    Inherit from : Port

    Fields :
        isImplicit :        Was this signal declared by the user or by some superior entity ?
    """

    isImplicit: bool = False


@dataclass(slots=True)
class Assignment(Element):
    """
    Store a constant assignment for a variable.

    Inherit from : Element

    Fields :
        - target :          The target signal name to be assigned.
        - source :          The list of the source signals to be involved into this assignment.
        - isComb :          Indicate that this assignment include more than a source, meaning the assignment require combinatorial logic. This will be evaluated for the output type.
    """

    target: str = ""
    source: list[str] = field(default_factory=list)
    isComb: bool = True


@dataclass(slots=True)
class Process(Element):
    """
    Store the different values for a single process / alway entry.

    Inherit from : Element

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


@dataclass(slots=True)
class Modport(Element):
    """
    Store a modport informations.
    This class could only be used in xVerilog parser.

    Inherit from : Element

    Fields :
        signals :           The list of ports objects to be defined within the selected modport.
    """

    signals: list[Port] = field(default_factory=list)


@dataclass(slots=True)
class Interface(Element):
    """
    Store the config for an interface entry.

    Inherit from : Element

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


@dataclass(slots=True)
class Module(Element):
    """
    Store the config for a known module, instantiated within the passed design.

    Inherit from : Element

    Fields :
        - entity :          The entity name of the included module.
        - connections :     A list of string tuples that match the port name and the actual connection name.
        - params :          The list of parameters passed to this module.
        - isVendor :        Does the module target something that looks like a vendor primitive ?
        - vendor :          The name of the vendor of this module, if applicable.
        - isConditionnal:   Is this module member of a conditionnal generate loop ?
        - isRepeated :      Is this module repeated in a for generate structure ?
        - count :           If fixed, the number of repetitions.
        - condition :       The condition for this instance to be instantiated.
    """

    entity: str = ""
    connections: list[tuple[str, str]] = field(default_factory=list)
    params: list[Parameter] = field(default_factory=list)
    isVendor: bool = False
    vendor: str = ""
    isConditionnal: bool = False
    isRepeated: bool = False
    count: str = "None"
    condition: str = "None"


@dataclass(slots=True)
class Function(Element):
    """
    Store the config for a known function, instantiated within the passed design.

    Inherit from : Element

    Fields :
        - func_inputs :     List of ports that are used as function inputs.
        - func_outputs :    List of ports that are used as function outputs.
    """

    func_inputs: list[Port] = field(default_factory=list)
    func_outputs: list[Port] = field(default_factory=list)


@dataclass(slots=True)
class FileInfo:
    """
    Store the different values for a single file info entry.
    Most of these fields are targeted by a git repo to be fetched, therefore it is the most complete within a repo.
    A fallback from the OS filesystem may be used.

    Inherit from : None

    Fields :
        - name :            The name of the file
        - path :            The path of the file
        - repo_path :       The path of the first parent of the git file. Used as title on the sections.
        - creation_author : The name of the author which created the file, ie the name of the first committer for this file. This field remain unresolved when the FS fallback is used.
        - creation_hash :   The hash of the first commit which affected this file. This field remain unresolved when the FS fallback is used.
        - creation_date :   The date of the first commit which was affected by this file. This field remain unresolved when the FS fallback is used.
        - creation_tag :    The first tag that was applied to this file. This field remain unresolved when the FS fallback is used.
        - edit_author :     The name of the latest author which committed this file. This field is resolved to the current user logged when building the doc. Therefore may be wrong for CICD based systems.
        - edit_hash :       The hash of the latest commit which included this file. This field remain unresolved when the FS fallback is used.
        - edit_date :       The date of the latest commit which included this file. This field is resolved to the latest date known to the OS.
        - edit_tag :        The latest tag of this file. This field remain unresolved when the FS fallback is used.
        - is_dirty :        Does this file contain changes that are not committed when building the doc ?
        - message :         The latest commit message.
    """

    name: str = ""
    path: str = ""
    repo_path: str = ""
    creation_author: str = ""
    creation_hash: str = ""
    creation_date: str = ""
    creation_tag: str = ""
    edit_date: str = ""
    edit_hash: str = ""
    edit_author: str = ""
    edit_tag: str = ""
    is_dirty: bool = False
    message: str = ""


@dataclass(slots=True)
class ComponentConfig:
    """
    Store additional elements for the Component object, that are more
    linked to the user config rather than pure HDL elements.

    Inherit from : None

    Fields :
        - warning :         Is there anything we need to add on the top of the page ?
        - notes :           Any notes to be added ?
        - isTestbench :     Define the current component as a testbench. This change some behaviors when the rendering pass is done*.
        - testbenchTarget : The name of the component to be tested. Only evaluated if this module is a testbench.
        - isPackage :       Define the current component as a package. This does change some behaviors when the rendering pass is done*.
        - isInterface:      Define the current component as an interface. This does change some behaviors when the rendering pass is done*.
        - constraints :     The different constraints to be applied to this module.
        - clock :           Define the clock and the associated frequency.
        - latency :         How many cycles will be needed for a result to be computed ?
        - throughput :      What's the throughput of the module ?
        - registers :       What's the register map of the module, if applicable ?
        - target:           Define the target to be used (Intel FPGA, Zynq ... ). Free string.
        - sim :             Did this module runned correctly on a simulator ?
        - tool :            The tool used to synth this module.
        - compliance:       Is this module compliant to any standard (PCIe, AXI ... ?)
        - burst :           Is there any forms of burst to be supported ?
        - security :        Does this module support any form of security options ?
        - status :          The status of the component. Could be any string, but standard (beta, release, stable ...) shall be preferred.
        - deprecrated:      Is the current module deprecated ? If yes, an alternative could be proposed.
        - version :         The version of the module.
        - task :            Insert here the current task this module is relevant to. Could be @task Project XX or @task Client YY
        - license:          Specify the license to be used.
        - copyright :       Is this module copyrighted to anything ?
        - tags :            A list of free tags to be used anywhere.

    * : Different elements may or may not be useful for the different kind of objects. Therefore, these flags are checking them
        to configure the optimal render method for the current component.
    """

    # @warning
    warning: str = ""

    # @notes
    notes: str = ""

    # @testbench
    isTestbench: bool = False

    # @target module_xx
    testbenchTarget: str = ""

    # @package
    isPackage: bool = False

    # @interface
    isInterface: bool = False

    # @constraint
    constraints: list[str] = field(default_factory=list)

    # @clock <name> <frequency>
    clock: list[tuple[str, int, str]] = field(default_factory=list)

    # @latency <cycles>
    latency: int = 0

    # @throughput <str>
    throughput: str = ""

    # @register <name> <offset> <size> <description>
    register: list[tuple[str, int, int, str]] = field(default_factory=list)

    # @target <name>
    target: str = ""

    # @tool <name>
    tool: str = ""

    # @sim <name>
    sim: str = ""

    # @compliance
    complicante: str = ""

    # @burst <size>
    burst: int = 0

    # @security <name>
    security: str = ""

    # @status released
    status: str = "release"

    # @deprecated <alternative>
    deprecated: str = ""

    # @version 1.0.0
    version: str = "1.0.0"

    # @task JIRA-928
    task: str = ""

    # @license
    license: str = ""

    # @copyright Altera Corp.
    copyright: str = ""

    # @tags Done
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Component:
    """
    Store all the infos for a component. Include all infos to be shared.

    Inherit from : None

    Fields :
        - file :            The FileInfo class that store all elements.
        - name :            The name of the component to be used.
        - brief :           The brief description of the component.
        - details :         The long description of the component.
        - config :          The extended config file to be used.
        - comp_type :       The component type, to eventually be inferred by the IR.

        - parameters :      The list of available parameters for this component.
        - ports :           The list of module ports.
        - enums :           The list of module enums.
        - imports :         The list of imports for the module.
        - signals :         The list of internal signals.
        - process :         The list of internal process within the module.
        - assigns :         The list of internal assignments.
        - interfaces :      The list of available interfaces. Only exposed when this file describe at least an interface.
        - modules :         The list of included elements within the design.
        - functions :       The list of functions the element may define.
        - structures :      The list of structures the element may define.

        - flags :           The list of unresolved flags, to be passed to the render stage(s).

        - isVendor :        Define the current component as a dependant of some vendors.
        - vendors :         Store the different vendors involved.
    """

    # ----------------------------------------------------------------------
    # FIELDS
    # ----------------------------------------------------------------------

    # File infos
    file: FileInfo

    # Basic infos
    name: str = ""
    brief: str = ""
    details: str = ""
    comp_type: str = ""

    # Render config
    config: ComponentConfig = field(default_factory=ComponentConfig)
    render: RTLConfig = field(default_factory=RTLConfig)

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
    functions: list[Function] = field(default_factory=list)
    structures: list[Structure] = field(default_factory=list)

    # Unknown flags
    flags: list[str] = field(default_factory=list)

    # ----------------------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------------------

    @property
    def vendors(self) -> set[str]:
        """Fetch the vendors known for the entity"""
        return {mod.vendor for mod in self.modules if mod.isVendor and mod.vendor}
