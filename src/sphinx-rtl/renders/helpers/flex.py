# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    06/10/2026
#
# Brief :   Build a flexbox table from a list of list
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx import addnodes


def render_flex_array(
    rows: list[
        list[
            nodes.Text
            | nodes.literal
            | nodes.inline
            | list[nodes.Node]
            | nodes.literal
            | nodes.paragraph
        ]
    ],
) -> nodes.container:
    """
    Build a flexbox array from a list of lists
    """

    # Safety
    if not rows:
        return nodes.container()

    # How many rows do we have ?
    max_cols = max(len(r) for r in rows)

    # Build the grid
    grid = nodes.container(classes=["sd-ms-3", "sd-my-2"])

    grid["style"] = (
        f"display: grid; "
        f"grid-template-columns: repeat({max_cols}, max-content); "
        f"column-gap: 0.5rem; "
        f"row-gap: 0rem; "
        f"align-items: center;"
    )

    for row in rows:

        for cell in row:
            grid += cell

        for _ in range(max_cols - len(row)):
            grid += nodes.inline()

    return grid
