# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Define the standard configurations elements to be used
#           within the project.
# ----------------------------------------------------------------------------

from dataclasses import dataclass, field
from pathlib import Path
import tomllib
import copy
from sphinx.util import logging

# Configure the logger
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------------------
@dataclass(slots=True)
class RTLConfig:
    """
    Configure the rendering process, to be able to match the user needs.

    Fields :
        - inferClocks :         Do we need to infer clocks for the different ports ?
        - inferResets :         Do we need to infer resets for the output ports ?
        - inferIOs :            Do we need to infer IO for the different processes ?
        - inferType:            Do we need to infer the component type (testbench, package, interface...) ?
        - inferPolarity :       Do we need to infer the polarity of the signals ?
        - inferGroups :         Do we need to groups the ports and signals following that start similar ?
        - inferAssignments:     Do we need to infer the constant assignments ?
        - resolveModules:       Do we need to infer the submodules IO types to ourselves ?
        - showSource :          Do we need to show the source file ?
        - mermaid :             Do we need to load the mermaid render from a CDN ?
        - wavedrom :            Do we need to load wavefrom render from a CDN ?
        - template :            Do we need to add a template instantiation at the end of the doc ?
        - signals :             Do we need to show all signals in the doc ?
        - internals :           Do we need to show all the internals (Processes, Enums, Imports ...) in the doc ? Setting this will also infer @nosignals.
        - inferVendor :         Do we need to infer the vendor from the different modules ?
        - vendor :              User available config to set the vendor manually.

        - public_output:        The stripped component output as JSON. Useful for NDA elements where not all documentation shall be exported.
        - private_output:       The internal fully detailed export as JSON. Useful for internal usage.
        - external_stubs:       The import stubs to be used for the rendering pass. Useful to import external component under any restrictions without comprising the quality of the infer pass.
    """

    # @noclocks
    inferClocks: bool = True

    # @noresets
    inferResets: bool = True

    # @noio
    inferIOs: bool = True

    # @notype
    inferType: bool = True

    # @nopolarity
    inferPolarity: bool = True

    # @nogroups
    inferGroups: bool = True

    # @noassigns
    inferAssignments: bool = False

    # @noresolve
    resolveModules: bool = True

    # @nosource
    showSource: bool = True

    # @nomermaid
    mermaid: bool = True

    # @wavedrom
    wavedrom: bool = True

    # @notemplate
    template: bool = True

    # @nosignals
    signals: bool = True

    # @nointernals:
    internals: bool = True

    # @novendors
    inferVendor: bool = True

    # @vendor Altera
    vendor: list[str] = field(default_factory=list)

    # Global fields
    public_output: list[str] = field(default_factory=list)
    private_output: list[str] = field(default_factory=list)
    external_stubs: list[str] = field(default_factory=list)

    # ----------------------------------------------------------------------------
    # FUNCTIONS
    # ----------------------------------------------------------------------------
    def merge(self, override: RTLConfig) -> RTLConfig:
        """
        Merge two elements into ourselves, and return a copy of us.
        """

        # Merge the elements
        self.inferClocks = self.inferClocks and override.inferClocks
        self.inferResets = self.inferResets and override.inferResets
        self.inferIOs = self.inferIOs and override.inferIOs
        self.inferType = self.inferType and override.inferType
        self.inferPolarity = self.inferPolarity and override.inferPolarity
        self.inferGroups = self.inferGroups and override.inferGroups
        self.inferAssignments = self.inferAssignments and override.inferAssignments
        self.resolveModules = self.resolveModules and override.resolveModules
        self.showSource = self.showSource and override.showSource
        self.mermaid = self.mermaid and override.mermaid
        self.wavedrom = self.wavedrom and override.wavedrom
        self.template = self.template and override.template
        self.signals = self.signals and override.signals
        self.internals = self.internals and override.internals
        self.inferVendor = self.inferVendor and override.inferVendor
        self.vendor = list(set(self.vendor) | set(override.vendor))

        # Return a copy
        return copy.deepcopy(self)

    def configure_infer(
        self,
        clocks: bool = True,
        resets: bool = True,
        IOs: bool = True,
        types: bool = True,
        polarity: bool = True,
        groups: bool = True,
        assignments: bool = True,
        vendor=True,
    ) -> None:
        """
        Configure the infer process elements.
        """
        self.inferClocks = clocks
        self.inferResets = resets
        self.inferIOs = IOs
        self.inferType = types
        self.inferPolarity = polarity
        self.inferGroups = groups
        self.inferAssignments = assignments
        self.inferVendor = vendor

    def configure_resolution(self, modules: bool = True) -> None:
        """
        Configure the plugin resolution
        """
        self.resolveModules = modules

    def configure_shown_elements(
        self,
        source: bool = True,
        mermaid: bool = True,
        wavedrom: bool = True,
        template: bool = True,
        signals: bool = True,
        internals: bool = True,
    ) -> None:
        """
        Configure the shown elements.
        """
        self.showSource = source
        self.mermaid = mermaid
        self.wavedrom = wavedrom
        self.template = template
        self.signals = signals
        self.internals = internals

    def add_vendor(self, vendor: str | list[str]) -> None:
        """
        Add a vendor to the internal database.
        """
        if type(vendor) is str:
            self.vendor.append(vendor)
        elif type(vendor) is list:
            self.vendor.extend(vendor)

    def add_public_output(self, output: str | list[str]) -> None:
        """
        Add an output of the public type (fully detailed JSON).
        """
        if type(output) is str:
            self.public_output.append(output)
        elif type(output) is list:
            self.public_output.extend(output)

    def add_private_output(self, output: str | list[str]) -> None:
        """
        Add an output of the private type (limited JSON).
        This output can be customized by the associated event.
        """
        if type(output) is str:
            self.private_output.append(output)
        elif type(output) is list:
            self.private_output.extend(output)

    def add_component_source(self, source: str | list[str]) -> None:
        """
        Add an external database to be loaded before performing the IR.
        This enable sharing data where the source must not be available to all.
        """
        if type(source) is str:
            self.external_stubs.append(source)
        elif type(source) is list:
            self.external_stubs.extend(source)
