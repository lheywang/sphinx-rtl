# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Define the standard configurations elements to be used
#           within the project.
# ----------------------------------------------------------------------------

from dataclasses import dataclass, field


@dataclass
class RenderConfig:
    """
    Configure the rendering process, to be able to match the user needs.

    Fields :
        - inferClocks :         Do we need to infer clocks for the different ports ?
        - inferResets :         Do we need to infer resets for the output ports ?
        - inferIOs :            Do we need to infer IO for the different processes ?
        - resolution :          Do we need to resolve the different modules ?
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

    # nosourceresolution
    resolution: bool = True

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
    vendor: str = ""
