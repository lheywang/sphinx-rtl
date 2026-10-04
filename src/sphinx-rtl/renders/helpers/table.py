# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    30/09/2026
#
# Brief :   Build a table from the provided data
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes


def render_table_header(
    headers: list[str],
    classes: list[str] | None = None,
    widths: list[int] | None = None,
) -> tuple[nodes.container, nodes.table]:
    """
    Initialise a table header
    """

    # Wrapper for the auto width scrolling
    wrapper = nodes.container(is_div=True, classes=["rtl-table-wrapper"])

    # Standard table
    num_cols = len(headers)
    table_classes = [
        "sd-table",
        "sd-table-hover",
        "sd-w-100",
    ]
    if classes:
        table_classes.extend(classes)

    table = nodes.table(classes=table_classes)
    tgroup = nodes.tgroup(cols=num_cols)
    table += tgroup

    # Build the columns
    for index in range(num_cols):
        if widths is not None and (index < len(widths)):
            tgroup += nodes.colspec(colwidth=widths[index])
        else:
            tgroup += nodes.colspec(colwidth=1)

    # Create table header
    thead = nodes.thead()
    head_row = nodes.row()
    for h in headers:
        entry = nodes.entry(classes=["sd-fw-bold"])
        p = nodes.paragraph(classes=["sd-m-0"])
        p += nodes.Text(h)
        entry += p
        head_row += entry
    thead += head_row
    tgroup += thead

    # Build the body
    tbody = nodes.tbody()
    tgroup += tbody

    # Add ourselves inside the wrapper
    wrapper += table

    return wrapper, table


def render_table_line(
    table: nodes.table,
    cells: list[nodes.Text | nodes.inline | list[nodes.Node] | str],
    row_classes: list[str] | None = None,
) -> nodes.row:
    """
    Add a row to the line
    """
    tbody = table.next_node(nodes.tbody)
    if tbody is None:
        raise ValueError("Unable to found a valid body for the table")

    row = nodes.row(classes=row_classes or [])

    for cell in cells:
        entry = nodes.entry()

        if isinstance(cell, str):
            p = nodes.paragraph(classes=["sd-m-0"])
            p += nodes.Text(cell)
            entry += p
        elif isinstance(cell, nodes.paragraph):
            entry += cell
        elif isinstance(cell, nodes.Node):
            p = nodes.paragraph(classes=["sd-m-0"])
            p += cell
            entry += p
        elif isinstance(cell, list):
            p = nodes.paragraph(classes=["sd-m-0"])
            p.extend(cell)
            entry += p

        row += entry

    tbody += row
    return row
