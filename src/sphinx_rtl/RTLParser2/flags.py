# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    03/11/2026
#
# Brief :   Fetch and apply flags from the source to a configuration class.
# ----------------------------------------------------------------------------

# Imports
import re

from sphinx.util import logging

from sphinx_rtl.models import Comment, ComponentConfig
from sphinx_rtl.RTLConfig import RTLConfig

from .utils import apply_flags_render, apply_flags_cfg

# Compile the flag
FLAG_RE = re.compile(r"^[ \t]*@(\w+)[ \t]*(.*)$")

# Configure the logger
logger = logging.getLogger(__name__)


def extract_flags(comment: Comment) -> tuple[ComponentConfig, RTLConfig]:

    # Extract the flags
    flags = []
    kept = []
    for i, raw in enumerate(comment.content.splitlines()):
        raw = re.sub(r"^\s*//+", "", raw)
        if m := FLAG_RE.match(raw):
            flags.append(
                {
                    "name": m.group(1),
                    "args": m.group(2).strip(),
                    "line": i,
                }
            )
        else:
            kept.append(raw)

    # Process the flags to bind them into the config
    cfg = ComponentConfig()
    warns = apply_flags_cfg(cfg, flags)

    # Print the warnings
    for warn in warns:
        logger.warning(warn)

    rtl = RTLConfig()
    warns = apply_flags_render(rtl, flags)

    # Print the warnings
    for warn in warns:
        logger.warning(warn)

    # Update the final comment content without the flags
    comment.content = "\n".join(kept)

    # Return both config
    return cfg, rtl
