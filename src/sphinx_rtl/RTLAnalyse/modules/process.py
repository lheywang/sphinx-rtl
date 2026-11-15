# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    27/09/2026
#
# Brief :   Fetch the process read and writes signals
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import Component


def infer_process(component: Component) -> Component:
    """
    Infer the signals the process use as inputs.
    """

    # First, fetch the list of inputs ports and the signals (which could be read and write)
    inputs = set([x.name for x in component.ports if x.direction in ["input", "inout"]])
    inputs |= set([x.name for x in component.signals])

    # Prepare two dicts for later
    signals = dict([(x.name, x) for x in component.signals])
    ports = dict([(x.name, x) for x in component.ports])

    # Now, fetch the process inputs :
    for process in component.process:
        process_inputs = set(process.signals)
        process.signals = list(process_inputs & inputs)

        # As the process read the signals, let's increment their counters
        for signal in process.signals:

            # Fetch the signal on the component
            source = signals.get(signal)
            if source is None:
                source = ports.get(signal)
            if source is None:
                continue

            # Increment the internal counter
            source.fanout += 1

    return component
