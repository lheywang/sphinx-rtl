# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    30/09/2026
#
# Brief :   Build a badges from the provided data
# ----------------------------------------------------------------------------

# Imports
from enum import StrEnum
from docutils import nodes


# Define the colors of the badge
class BadgeColor(StrEnum):
    BLUE = "primary"
    BLUE_LINE = "primary-line"
    GREEN = "success"
    GREEN_LINE = "success-line"
    CYAN = "info"
    CYAN_LINE = "info-line"
    ORANGE = "warning"
    ORANGE_LINE = "warning-line"
    RED = "danger"
    RED_LINE = "danger-line"
    LIGHT_GRAY = "light"
    GRAY = "muted"
    GRAY_LINE = "muted-line"
    DARK_GRAY = "dark"
    DARK_GRAY_LINE = "dark-line"
    WHITE = "white"
    BLACK = "black"
    BLACK_LINE = "black-line"


def render_badge(
    label: str,
    color: BadgeColor,
    outline: bool = True,
    pill: bool = True,
) -> nodes.inline:
    """
    Build a badge from the provided elements
    """
    classes = ["sd-badge"]
    if outline:
        classes.extend([f"sd-outline-{color}", f"sd-text-{color}"])
    else:
        classes.extend([f"sd-bg-{color}", "sd-text-white"])

    if pill:
        classes.append("sd-rounded-pill")

    return nodes.inline(label, label, classes=classes)
