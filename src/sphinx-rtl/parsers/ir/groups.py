# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    28/09/2026
#
# Brief :   Assign the port and signals groups for a better understanding.
# ----------------------------------------------------------------------------

# Imports
from ...models import Component
from collections import Counter, defaultdict

# Configure logger
from sphinx.util import logging
from typing import TypeVar

# Get a free type variable
T = TypeVar("T")

logger = logging.getLogger(__name__)


def _infer(names: list[str], elements: list[T]):
    parsed = [(p.split("_"), p) for p in sorted(names)]

    # Count the different elements for the different paths.
    counts: Counter[str] = Counter()
    for parts, _ in parsed:
        for i in range(1, len(parts)):
            path = "/".join(parts[:i])
            counts[path] += 1

    # Build the groups
    groups: dict[str, list[str]] = defaultdict(list)
    for parts, port in parsed:
        assigned = False

        # Start from the most specific to the least
        for i in range(len(parts) - 1, 0, -1):
            path = "/".join(parts[:i])
            if counts[path] >= 2:
                groups[path].append(port)
                assigned = True
                break

        # Ensure orphans
        if not assigned:
            groups[""].append(port)

    # Finally. By using a dict, we ensure a O(1) search, rather than an 0(N2) time...
    port_groups = dict()
    for group, ports in groups.items():
        for port in ports:
            port_groups[port] = group

    # Match the ports
    for element in elements:
        element.group = port_groups[element.name]  # type: ignore

    # Add some logs here
    groups_count = len(groups.keys())
    if groups_count > 1:
        logger.info(
            f"[INFO] Found {groups_count} group{"s" if groups_count > 1 else ""}"
        )


def infer_groups(component: Component) -> Component:
    """
    Infer the port and signals groups based on their names.
    """
    # First, infer the ports groups
    port_names = [p.name for p in component.ports]
    _infer(port_names, component.ports)

    # Then, infer the signals groups
    signals_names = [p.name for p in component.signals]
    _infer(signals_names, component.signals)

    return component
