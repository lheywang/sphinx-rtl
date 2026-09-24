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
    """

    name: str = ""
    description: str = ""
    line: int = -1


@dataclass
class Parameter(Element):
    """
    Store the different values for a single parameter (or generic in VHDL) entry.
    """

    hdl_type: str = ""
    hdl_value: str = ""


@dataclass
class Port(Element):
    """
    Store the different values for a single port entry.
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
    """

    values: list[int] = field(default_factory=list)
    members: list[str] = field(default_factory=list)


@dataclass
class Import(Element):
    """
    Store the different values for a single import (Verilog Only) entry.
    """

    target: str = ""


@dataclass
class Signal(Element):
    """
    Store the different values for a single single reg / wire (or signal in VHDL) entry.
    """

    hdl_type: str = ""
    hdl_size: list[str] = field(default_factory=list)
    hdl_value: str = ""


@dataclass
class Assignment(Element):
    """
    Store a constant assignment for a variable.
    """

    target: str = ""
    source: list[str] = field(default_factory=list)
    isComb: bool = True


@dataclass
class Process(Element):
    """
    Store the different values for a single process / alway entry.
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
    """

    signals: list[Port] = field(default_factory=list)


@dataclass
class Interface(Element):
    """
    Store the config for an interface entry.
    """

    parameters: list[Parameter] = field(default_factory=list)
    ports: list[Port] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    modports: list[Modport] = field(default_factory=list)


@dataclass
class Module(Element):
    """
    Store the config for a known module, instantianed within the passed design.
    """

    entity: str = ""
    connections: list[tuple[str, str]] = field(default_factory=list)
    params: list[Parameter] = field(default_factory=list)
    isVendor: bool = False
    vendor: str = ""


@dataclass
class FileInfo:
    """
    Store the different values for a single file info entry
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
class Component:
    """
    Store all the infos for a component. Include all infos to be shared.
    """

    # File infos
    file: FileInfo

    # Basic infos
    name: str = ""
    brief: str = ""
    details: str = ""

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
