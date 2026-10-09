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
        - showSource :          Do we need to show the source file ?
        - mermaid :             Do we need to load the mermaid render from a CDN ?
        - wavedrom :            Do we need to load wavefrom render from a CDN ?
        - template :            Do we need to add a template instantiation at the end of the doc ?
        - signals :             Do we need to show all signals in the doc ?
        - internals :           Do we need to show all the internals (Processes, Enums, Imports ...) in the doc ? Setting this will also infer @nosignals.
        - inferVendor :         Do we need to infer the vendor from the different modules ?
        - vendor :              User available config to set the vendor manually.
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

    @classmethod
    def discover(cls, base_path: Path) -> RTLConfig:
        """
        Discover and self-load the first sphinx-rtl.toml file to be found.
        """

        # Init elements
        current = base_path.resolve()
        toml_path: Path | None = None

        # Iterate until we find something
        for parent in [current, *current.parents]:
            candidate = parent / "sphinx-rtl.toml"
            if candidate.is_file():
                toml_path = candidate
                break

        if not toml_path:
            logger.warning(
                "Could not find any sphinx-rtl.toml file. Using default config."
            )
            return cls()

        logger.info(f"[INFO] Found config file at {str(toml_path)}. Using it.")

        # Loading the parameters :
        try:
            with toml_path.open("rb") as f:
                data = tomllib.load(f).get("rtl", {})

            init = cls()
            for key, value in data.items():
                try:
                    setattr(init, key, value)
                except AttributeError as e:
                    pass
            return init

        except Exception as e:
            logger.error(f"[ERROR] Could not load the config file. Reason : {e}")
            return cls()

    def merge(self, override: RTLConfig) -> RTLConfig:
        """
        Merge two elements into ourselves, and return a copy of us.
        """

        # Merge the elements
        self.inferClocks = self.inferClocks or override.inferClocks
        self.inferResets = self.inferResets or override.inferResets
        self.inferIOs = self.inferIOs or override.inferIOs
        self.inferType = self.inferType or override.inferType
        self.inferPolarity = self.inferPolarity or override.inferPolarity
        self.inferGroups = self.inferGroups or override.inferGroups
        self.showSource = self.showSource or override.showSource
        self.mermaid = self.mermaid or override.mermaid
        self.wavedrom = self.wavedrom or override.wavedrom
        self.template = self.template or override.template
        self.signals = self.signals or override.signals
        self.internals = self.internals or override.internals
        self.inferVendor = self.inferVendor or override.inferVendor
        self.vendor = list(set(self.vendor) | set(override.vendor))

        # Return a copy
        return copy.deepcopy(self)
