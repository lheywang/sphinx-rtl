# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    20/10/2026
#
# Brief :   Define utilities to interact with the Nodes.
# ----------------------------------------------------------------------------

# Imports
from tree_sitter import Node, QueryCursor


def get_text(node: Node, source: bytes):
    """
    Return the text associated to nodes from the source file.
    """
    if node is None:
        return ""
    return source[node.start_byte : node.end_byte].decode("utf-8").strip()


def get_line(node: Node) -> int | tuple[int, int]:
    """
    Return the line tuple of a Node, using start and stop. Easier to use than the fixed one int line.
    """
    if node is None:
        return -1

    start = node.start_point[0]
    stop = node.end_point[0]

    # If the line "ends" on the first char, let's go back one upper.
    if node.end_point[1] == 0:
        stop -= 1

    if start != stop:
        return (start, stop)
    return start


def get_identifiers(node: Node, source: bytes) -> list[str]:
    """
    Extract all identifiers recursively.
    """
    identifiers = []
    vhdl_control_words = {"when", "else", "true", "false", "null", "open", "all"}

    def traverse(n: Node):
        if n.type == "identifier":
            text = source[n.start_byte : n.end_byte].decode("utf-8")
            if text.lower() not in vhdl_control_words and text not in identifiers:
                identifiers.append(text)
        for child in n.children:
            traverse(child)

    traverse(node)
    return identifiers


def collect(query, container):
    """
    Collect data from a provided container and query.

    Used for 2nd layers queries.
    """

    # If empty, return nothing.
    if container is None:
        return []

    for _, caps in QueryCursor(query).matches(container):
        conn = caps["conn"][0]
        yield (
            {
                "node": conn,
                "kind": conn.type,
                "name": caps["name"][0] if "name" in caps else None,
                "value": caps["value"][0] if "value" in caps else None,
                "wildcard": conn.type == "dot_star_port_connection",
            }
        )
