# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    22/10/2026
#
# Brief :   Define the comment linker function, to associate comments
#           to IR objects.
# ----------------------------------------------------------------------------

# Imports
import sys
from typing import Sequence
from sphinx.util import logging
from sphinx._cli.util.colour import blue

from sphinx_rtl.models import Comment, Component, ALL_MODELS

# Configure logger
logger = logging.getLogger(__name__)


# Helper
def get_distance(
    comment: tuple[int, int] | int, statement: tuple[int, int] | int
) -> int:
    """
    Return the distance between these two objects.
    The distance is calculated as :

    For tuples :
        comment[1] - statement[0].
    else :
        comment - statement.

    (A mix is possible and supported)
    """

    comment_line: int = comment[0] if isinstance(comment, tuple) else comment
    statement_line: int = statement[0] if isinstance(statement, tuple) else statement

    # Barrier against uninitialized values. Could return 0 if both are -1, which is NOT correct.
    if comment_line == -1 or statement_line == -1:
        return sys.maxsize

    return comment_line - statement_line


def recursive_iterative_assignment(
    elements: Sequence[ALL_MODELS] | ALL_MODELS, comments: list[Comment], count: int = 0
) -> int:
    """
    Iterate over the elements
    """

    # First, do we have something to assign ?
    for element in elements:

        for comment in list(comments):

            d = get_distance(comment.line, element.line)

            if -3 <= d <= 1:
                element.description = comment.content
                comments.remove(comment)
                count += 1
                break

        # Is there some childs that need linking ?
        count = recursive_iterative_assignment(element, comments, count)

    # Return the count
    return count


# Main function
def link_comments(source: list[Comment], elements: dict[str, Component]) -> None:
    """
    Perform an iterative linking between the comments and the objects found.
    """

    # First, fetch the first comment and extract
    header = ""
    if isinstance(source[0].line, tuple):
        target = source[0].line[0]
    else:
        target = source[0].line

    if target == 0:
        header = source[0].content
        source.remove(source[0])

    # Try to make sense from the header ?
    brief = details = ""
    if "\n" in header:
        brief, details = [x.strip() for x in header.split("\n", 1)]
    elif "." in header:
        brief, details = [x.strip() for x in header.split(".", 1)]
    else:
        brief = header.strip()

    for element in elements.values():

        # Update the elements
        element.brief = brief
        element.details = details

        # Do the recursive linking
        count = 0
        count += recursive_iterative_assignment(element.parameters, source)
        count += recursive_iterative_assignment(element.ports, source)
        count += recursive_iterative_assignment(element.enums, source)
        count += recursive_iterative_assignment(element.signals, source)
        count += recursive_iterative_assignment(element.imports, source)
        count += recursive_iterative_assignment(element.process, source)
        count += recursive_iterative_assignment(element.assigns, source)
        count += recursive_iterative_assignment(element.interfaces, source)
        count += recursive_iterative_assignment(element.modules, source)
        count += recursive_iterative_assignment(element.functions, source)
        count += recursive_iterative_assignment(element.structures, source)

        # Add some logs
        logger.info(blue(f"[INFO] Attached {count} comments to {element.name}."))

    logger.info(
        blue(f"[INFO] Could not fine an object to assign for {len(source)} comments.")
    )
