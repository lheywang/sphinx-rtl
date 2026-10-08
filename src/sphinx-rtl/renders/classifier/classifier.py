# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    08/10/2026
#
# Brief :   Classify module for the ports and signals.
# ----------------------------------------------------------------------------

# Imports
from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar("T")


@dataclass
class GroupNode(Generic[T]):
    """
    Store the data about a specific group, as a node tree.
    """

    name: str = ""
    items: list[T] = field(default_factory=list)
    children: dict[str, GroupNode[T]] = field(default_factory=dict)

    @property
    def count(self) -> int:
        """
        Return the count of the items inside this node !
        """
        return len(self.items) + sum(child.count for child in self.children.values())

    def compress(self) -> None:
        """
        Compress the empty nodes to ensure an easy print.
        """

        # Compress all the children.
        for child in self.children.values():
            child.compress()

        # Compress ourselves:
        if not self.items and len(self.children) == 1 and self.name:
            only_name, only_child = next(iter(self.children.items()))
            self.name = f"{self.name}/{only_name}"
            self.items = only_child.items
            self.children = only_child.children


class ElementClassifier(Generic[T]):
    """
    Build the tree for a compress hierarchy from an element collection.
    """

    def __init__(self, path_extractor: Callable[[T], str] | None = None) -> None:
        self._path_extractor = path_extractor or (lambda x: getattr(x, "group", ""))

    def build_tree(self, elements: Iterable[T]) -> GroupNode[T]:
        """
        Build the compressed tree from the elements.
        """
        root: GroupNode[T] = GroupNode()

        # Add the elements
        for item in elements:
            raw_path = self._path_extractor(item)
            parts = [p for p in raw_path.split("/") if p]
            self._insert(root, parts, item)

        # Compress the tree
        root.compress()
        return root

    def _insert(self, node: GroupNode[T], parts: list[str], item: T) -> None:
        """
        Insert an item into the specified location on the root
        """

        # Do we have parts to append ?
        if not parts:
            node.items.append(item)
            return

        # Do we need to create a new node ?
        head, *tail = parts
        if head not in node.children:
            node.children[head] = GroupNode(name=head)

        # Insert it
        self._insert(node.children[head], tail, item)
