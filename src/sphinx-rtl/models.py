# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the standard interface between the different parsers for the
#           different supported languages.
# ----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class Parameter:
    """
    Store the different values for a single parameter (or generic in VHDL) entry.
    """

    name: str
    hdl_type: str
    hdl_value: str = ""
    description: str = ""


@dataclass
class Port:
    """
    Store the different values for a single port entry.
    """

    name: str
    direction: str
    hdl_type: str
    description: str = ""


@dataclass
class Enum:
    """
    Store the different values for single enumeration (or type in VHDL) entry.
    """

    name: str
    values: list[str]
    description: str = ""


@dataclass
class Imports:
    """
    Store the different values for a single import (Verilog Only) entry.
    """

    name: str
    description: str = ""


@dataclass
class Signal:
    """
    Store the different values for a single single reg / wire (or signal in VHDL) entry.
    """

    name: str
    hdl_type: str
    hdl_value: str = ""
    hdl_attribute: str = ""
    hdl_value: str = ""
    description: str = ""


@dataclass
class FileInfo:
    """
    Store the different values for a single file info entry
    """

    name: str
    path: str
    author: str
    creation_hash: str
    edit_date: str
    creation_date: str
    edit_date: str


@dataclass
class Component:
    """
    Store all the infos for a component. Include all infos to be shared.
    """

    # Basic infos
    name: str
    brief: str
    details: str

    # File infos
    file: FileInfo

    # HDL elements
    parameters: list[Parameter]
    ports: list[Port]
    enums: list[Enum]
    imports: list[Imports]
    signals: list[Signal]
