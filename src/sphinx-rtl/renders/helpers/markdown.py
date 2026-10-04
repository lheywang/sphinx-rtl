# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    04/10/2026
#
# Brief :   Convert a text stream formatted as markdown into a series of nodes.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes, utils
from myst_parser.parsers.docutils_ import Parser

md_parser = Parser()


def render_markdown(text: str) -> list[nodes.Node]:
    """
    Convert a markdown string to a series of docutils nodes
    """
    if not text or not text.strip():
        return [nodes.paragraph(text="-")]

    document = utils.new_document("")
    md_parser.parse(text.strip(), document)

    return list(document.children)
