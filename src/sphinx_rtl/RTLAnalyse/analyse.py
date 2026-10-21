# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    09/10/2026
#
# Brief :   Handle the config for our rendering pass
# ----------------------------------------------------------------------------

# Imports
from graphlib import CycleError, TopologicalSorter
from sphinx.util import logging
from sphinx._cli.util.colour import bold, blue
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx_rtl.models import Component, RTLConfig, FileInfo
import time

from .modules import (
    infer_assigns,
    infer_clocks,
    infer_groups,
    infer_type,
    infer_polarity,
    infer_process,
    infer_resets,
    infer_vendors,
    infer_submodules,
)

# Configure the logger
logger = logging.getLogger(__name__)


# Class
class RTLAnalyse:
    """
    Handle the analyse of the different components within the project.
    """

    # --------------------------------------------------------------------------------
    # PUBLIC FUNCTIONS
    # --------------------------------------------------------------------------------

    def __init__(self, app: Sphinx, env: BuildEnvironment):
        """
        Build the analyse class.
        """

        # Fetch the sphinx elements
        self.app = app
        self.env = env

    def analyse(self, components: dict[str, Component]):
        """
        Launch the analysis of the different components, following the best order to ensure no elements will be forgotten.
        """

        # First, logs.
        logger.info(
            bold(
                f"[INFO] Running analysis for {len(components)} component{"s" if len(components) > 1 else ""}"
            )
        )

        # Emit an event before doing anything
        self.app.emit("rtl-pre-analysis", self.app, self.env, components)

        # Then, build the component internal dict
        component_order = self._sort(components)

        # Iterating over the components
        for component in component_order:

            try:
                target = components.get(component)
                if target is not None:
                    output = self._analyse_component(target, components)
                    components[component] = output
                else:
                    logger.warning(
                        f"Could not fetch a component from the global dict. Ignoring analysis."
                    )
            except Exception as e:
                logger.error(f"Failed to analyse component {component} : {e}")

        # Emit an event before returning
        self.app.emit("rtl-pre-analysis", self.app, self.env, components)
        return

    # --------------------------------------------------------------------------------
    # PRIVATE FUNCTIONS
    # --------------------------------------------------------------------------------
    def _sort(self, components: dict[str, Component]) -> list[str]:
        """
        Sort the components to optimize the analysis while ensuring no information will be forgotten.
        """

        # Build the sorter
        sorter = TopologicalSorter()

        # Allocate memory for the output
        order: list[str] = []

        # Build the tree
        for name, component in components.items():

            # Add ourselves as a node.
            sorter.add(name)

            for modules in component.modules:
                sorter.add(component.name, modules.entity)

        # Fetch the order
        try:
            order = list(sorter.static_order())
        except CycleError as err:
            cycle_chain = " -> ".join(err.args[1])
            logger.error(
                f"Could not determine order due to the cycle error : {cycle_chain}. No module will be analyzed."
            )
            return []

        # Return the elements
        return order

    def _analyse_component(
        self, component: Component, all: dict[str, Component]
    ) -> Component:
        """
        Perform the analysis from a single component, according the passed configuration element.
        """
        logger.info(bold(f"[INFO] --- Running analysis for {component.name}."))
        ts = time.time()

        cfg: RTLConfig = component.render

        # ------------------------------
        # INFER IOs
        # ------------------------------
        if cfg.inferIOs:

            # Inferring processes are required for the others to operate properly.
            component = infer_process(component)

            # ------------------------------
            # INFER CLOCKS
            # ------------------------------
            if cfg.inferClocks:
                component = infer_clocks(component)

            # ------------------------------
            # INFER RESETS
            # ------------------------------
            if cfg.inferResets:
                component = infer_resets(component)

            # Finally infer assignments.
            component = infer_assigns(component)

        else:
            if cfg.inferClocks:
                logger.warning(
                    "Could not infer clocks. IO inferring is required for this feature to be available."
                )
            if cfg.inferResets:
                logger.warning(
                    "Could not infer resets. IO inferring is required for this feature to be available."
                )

        # ------------------------------
        # GROUP SIGNALS
        # ------------------------------
        if cfg.inferGroups:
            component = infer_groups(component)

        # ------------------------------
        # INFER POLARITY
        # ------------------------------
        if cfg.inferPolarity:
            component = infer_polarity(component)

        # ------------------------------
        # INFER COMPONENT TYPE
        # ------------------------------
        if cfg.inferType:
            component = infer_type(component)

        # ------------------------------
        # INFER MODULE RESOLUTION
        # ------------------------------
        if cfg.resolveModules:
            component = infer_submodules(component, all)

        # ------------------------------
        # INFER VENDORS
        # ------------------------------
        if cfg.inferVendor:
            component = infer_vendors(component)

            # Re-assigning assigns may be needed then
            component = infer_assigns(component)

        # Final logs
        tt = time.time()
        logger.info(
            blue(
                f"[INFO] Finished analysis for {component.name} in {(tt - ts) * 1000:.1f} ms."
            )
        )
        return component
