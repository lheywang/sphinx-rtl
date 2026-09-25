# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    24/09/2026
#
# Brief :   Assemble a sub element of the standard module.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast
from pyslang import SourceManager

from ...models import Interface, Port, Parameter, Modport, Signal
from .parameter import build_parameter
from .port import build_port
from .signal import build_signal
from .modport import build_modport


def build_interface(
    node: ast.InstanceSymbol, line: int, sm: SourceManager
) -> Interface:
    """
    Build an interface from the passed node.
    """
    body: ast.InstanceBodySymbol = node.body
    name = body.definition.name

    # Init the outputs
    ports: list[Port] = []
    parameters: list[Parameter] = []
    signals: list[Signal] = []
    modports: list[Modport] = []

    # Extract the signals
    port_names: list[str] = []
    for elem in node.body:

        current_line = sm.getLineNumber(elem.location)
        if current_line == 0:
            current_line = -1

        match elem.kind:
            case ast.SymbolKind.Parameter:
                parameters.append(build_parameter(elem, current_line))

            case ast.SymbolKind.Port:
                port_names.append(elem.name.strip())
                ports.append(build_port(Port(), elem, current_line))

            case ast.SymbolKind.Variable:
                if elem.name.strip() not in port_names:
                    signals.append(build_signal(elem, current_line))

            case ast.SymbolKind.Modport:
                modports.append(build_modport(elem, current_line, sm))

    # Build the object and return it
    return Interface(name=name, line=line, parameters=parameters, ports=ports)
