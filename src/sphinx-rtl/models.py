# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the standard interface between the different parsers for the
#           different supported languages.
# ----------------------------------------------------------------------------

from dataclasses import dataclass, field


@dataclass
class Parameter:
    """
    Store the different values for a single parameter (or generic in VHDL) entry.
    """

    name: str = ""
    hdl_type: str = ""
    hdl_value: str = ""
    description: str = ""
    line: int = -1


@dataclass
class Port:
    """
    Store the different values for a single port entry.
    """

    name: str = ""
    direction: str = ""
    hdl_type: str = ""
    hdl_size: list[str] = field(default_factory=list)
    hdl_sync: str = ""
    hdl_reset: str = ""
    description: str = ""
    line: int = -1


@dataclass
class Enum:
    """
    Store the different values for single enumeration (or type in VHDL) entry.
    """

    name: str = ""
    values: list[int] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    description: str = ""
    line: int = -1


@dataclass
class Import:
    """
    Store the different values for a single import (Verilog Only) entry.
    """

    name: str = ""
    description: str = ""
    line: int = -1


@dataclass
class Signal:
    """
    Store the different values for a single single reg / wire (or signal in VHDL) entry.
    """

    name: str = ""
    hdl_type: str = ""
    hdl_size: list[str] = field(default_factory=list)
    hdl_value: str = ""
    description: str = ""
    line: int = -1


@dataclass
class Assignment:
    """
    Store a constant assignment for a variable.
    """

    target: str = ""
    source: list[str] = field(default_factory=list)
    isComb: bool = True
    description: str = ""
    line: int = -1


@dataclass
class Process:
    """
    Store the different values for a single process / alway entry.
    """

    name: str = ""
    hdl_type: str = ""
    signals_write: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    hdl_clock: list[str] = field(default_factory=list)
    hdl_reset: list[str] = field(default_factory=list)
    description: str = ""
    line: int = -1


@dataclass
class Modport:
    """
    Store a modport informations.
    """

    name: str = ""
    signals: list[Port] = field(default_factory=list)
    description: str = ""
    line: int = -1


@dataclass
class Interface:
    """
    Store the config for an interface entry.
    """

    name: str = ""
    parameters: list[Parameter] = field(default_factory=list)
    ports: list[Port] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    modports: list[Modport] = field(default_factory=list)
    description: str = ""
    line: int = -1


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
