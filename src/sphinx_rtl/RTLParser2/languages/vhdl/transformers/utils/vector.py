# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    20/10/2026
#
# Brief :   Return a built vector with all the informations needed.
# ----------------------------------------------------------------------------

# Imports
from tree_sitter import Node

from sphinx_rtl.RTLParser2.languages.utils import get_text, get_line

from .size_type import get_size_type


# Function
def get_vector(
    ids: Node, subtype: Node, source: bytes, init: Node | None = None
) -> list[tuple[int, str, str, list[str], str]]:
    """
    Return a formatted elements ready to be placed into a Signal / Port / Parameter / whatever is needed.

    Arguments :
        ids : ids Node from tree-sitter
        subtype : type Node from tree-sitter
        source : Raw source from file
        init : Optional Node from tree-sitter

    Returns
        line : Line where this element is found
        name : Name of the entity if applicable
        typ  : Type of the entity
        size : List of size element, ready to rendered.
        init : The init value.
    """

    # Fetch the line
    line = get_line(ids)

    # Fetch the identifiers
    ids_text = get_text(ids, source)
    names = [n.strip() for n in ids_text.split(",")]

    # Fetch they types
    typ = get_text(subtype, source)

    init_val = ""
    if init is not None:
        init_val = get_text(init, source).strip()

        if "others" in init_val.lower():
            val = init_val.split("'")[1]
            init_val = f"{val}{val}{val}...{val}{val}{val}"
        else:
            init_val = init_val.replace("'", "").replace('"', "").strip().split("=")[-1]

            if init_val.isnumeric():
                init_val = str(int(init_val.replace("'", "").split("=")[-1]))

    # Fetch size and type
    typ, size = get_size_type(typ)

    # Return
    rets = []
    for name in names:
        rets.append((line, name, typ, size, init_val))

    return rets
