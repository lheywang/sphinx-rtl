# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    08/10/2026
#
# Brief :   Render a tree of elements (ports and signals typically ...)
# ----------------------------------------------------------------------------

# Imports
from typing import Any, Callable, TypeVar, Generic
from docutils import nodes
from sphinx_rtl.RTLRender.classifier import GroupNode
from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_badge,
    render_dropdown,
    render_table_header,
)

# Define our custom type
T = TypeVar("T")


# Class
class TreeRenderer(Generic[T]):
    """
    Translate a tree of GroupNodes into a docutils nodes structure.
    """

    def __init__(
        self,
        headers: list[str],
        width: list[int],
        row_renderer: Callable[[nodes.table, T], None],
    ) -> None:
        """
        Instantiate a tree renderer element. Use a callback to customize the render aspect !
        """
        self.headers = headers
        self.width = width
        self.row_renderer = row_renderer

    def render(self, root: GroupNode[T], parent_container: nodes.Element) -> None:
        """
        Render a tree from the root node.
        """
        self._render_recursive(root, parent_container, is_root=True)

    def _render_recursive(
        self, node: GroupNode[T], parent_container: nodes.Element, is_root: bool
    ) -> None:
        """
        The recursive renderer engine, to append elements one after the other.
        """
        # Fetch the parent container.
        target_container = parent_container

        # Are we a child ?
        if not is_root:
            title = nodes.paragraph()
            title += nodes.Text(node.name)
            title += nodes.inline(" ", " ")
            title += render_badge(
                f"{node.count} element{'s' if node.count > 1 else ''}",
                BadgeColor.CYAN,
                outline=True,
            )

            dd, body = render_dropdown(title, is_open=False)
            parent_container += dd
            target_container = body

        # Do we have any items to add ?
        if node.items:
            table_body, table = render_table_header(self.headers, widths=self.width)
            target_container += table_body

            for item in node.items:
                self.row_renderer(table, item)

        # Render the childs
        for child in node.children.values():
            self._render_recursive(child, target_container, is_root=False)
