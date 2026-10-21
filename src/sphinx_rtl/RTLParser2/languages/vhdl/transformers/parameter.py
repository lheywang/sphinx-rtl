# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the Parameter transformer
# ----------------------------------------------------------------------------

# Import
from tree_sitter import Node

from sphinx_rtl.models import Parameter

from .utils import get_vector


# Functions
def VHDLTransformerParameter(
    index: int, nodes: dict[str, list[Node]], source: bytes
) -> Parameter | list[Parameter] | None:

    if index == 0:
        # Does it have the required properties ?
        if "param.ids" not in nodes or "param.subtype" not in nodes:
            return None

        # Build the vector
        elements: list[tuple[int, str, str, list[str], str]] = get_vector(
            nodes["param.ids"][0],
            nodes["param.subtype"][0],
            source,
            nodes["param.init"][0] if "param.init" in nodes else None,
        )

        # Build the object
        params: list[Parameter] = []
        for element in elements:
            line, name, typ, _, init = element
            params.append(
                Parameter(
                    name=name, line=line, hdl_type=typ, hdl_value=init, constant=False
                )
            )

        return params

    elif index == 1:

        # Does it have the required properties
        if "constant.node" not in nodes or "constant.names" not in nodes:
            return None

        # Build the vector
        elements: list[tuple[int, str, str, list[str], str]] = get_vector(
            nodes["constant.names"][0],
            nodes["constant.type"][0],
            source,
            nodes["constant.init"][0] if "constant.init" in nodes else None,
        )

        # Build the object
        params: list[Parameter] = []
        for element in elements:
            line, name, typ, _, init = element

            # Cleanup the init if needed (long)
            init = init.strip()

            if len(init) > 8:
                init = f"0x{int(init, 2)}"

            params.append(
                Parameter(
                    name=name, line=line, hdl_type=typ, hdl_value=init, constant=True
                )
            )

        return params

    else:
        return None
