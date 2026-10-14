# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Resolve the clocks that interract in both Read and Writes for
#           a port / signal
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import Component
import itertools

# Configure logger
from sphinx.util import logging
from sphinx._cli.util.colour import blue

logger = logging.getLogger(__name__)


def infer_submodules(component: Component, all: dict[str, Component]) -> Component:
    """
    Infer the signals parameters of the different submodules types...

    This function can be quite heavy, but also add a lot of the global documentation.
    """

    # Fetch the port and signals names :
    internal_names = dict(
        [(x.name, x) for x in itertools.chain(component.signals, component.ports)]
    )

    # Iterate over all the modules.
    count = 0
    submodules = 0
    for module in component.modules:

        # First, fetch the target module
        target = all.get(module.entity)

        if target is None:
            # Nothing to do ...
            continue

        # Get the list of all the signals and ports within the target
        target_ports = dict(
            [(x.name, x) for x in target.ports if x.direction == "output"]
        )
        submodules += 1

        # Now, bind them only if the ports is an output. Otherwise, the type couldn't (and must not !) be inferred.
        for target_name, internal_name in module.connections:

            # Do the port may be found on the target ?
            target_port = target_ports.get(target_name)
            internal_obj = internal_names.get(internal_name)

            # If both exists, we can copy the attributes (clock, resets) to the higher level
            if (target_port is not None) and (internal_obj is not None):
                internal_obj.hdl_sync = target_port.hdl_sync
                internal_obj.hdl_reset = target_port.hdl_reset
                count += 1

    # Logs
    if count > 0:
        logger.info(
            blue(
                f"[INFO] Copied properties of {count} port{"s" if count > 1 else ""} from {submodules} submodule{"s" if submodules > 1 else ""}"
            )
        )

    return component
