# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    22/10/2026
#
# Brief :   Merge single lines comments into wider objects. Useful before
#           the linking process.
# ----------------------------------------------------------------------------

# Imports
import sys
from sphinx.util import logging
from sphinx._cli.util.colour import blue

from sphinx_rtl.models import Comment

# Configure the logger
logger = logging.getLogger(__name__)


def comment_transformer(inp: list[Comment]) -> list[Comment]:
    """
    Links comments that are strictly contiguous on the file together, to make
    the linker easier (and faster !).
    """

    # Init memory
    count: int = 0
    initial_line: int = -sys.maxsize
    previous_line: int = -sys.maxsize
    output: list[Comment] = []

    # Loop over comments
    for comment in inp:

        # Does the comment need to be linked ?
        if comment.line == (previous_line + 1):

            if comment.merge_authorized == False:
                continue

            count += 1
            previous_line += 1
            output[-1].content = output[-1].content + "\n" + comment.content.strip()
            output[-1].line = (
                initial_line,
                (comment.line[0] if isinstance(comment.line, tuple) else comment.line),
            )

        else:
            output.append(comment)
            initial_line = previous_line = (
                comment.line[0] if isinstance(comment.line, tuple) else comment.line
            )

    # Finish with logs
    if count > 0:
        logger.info(
            blue(
                f"[INFO] Merged {count} single line comments into a multiline comment."
            )
        )

    return output
