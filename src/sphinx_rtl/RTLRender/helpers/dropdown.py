# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    30/09/2026
#
# Brief :   Build a badges from the provided data
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx_design.dropdown import dropdown_main, dropdown_title
from sphinx_design.icons import get_octicon


def render_dropdown(
    title: nodes.paragraph,
    is_open: bool = False,
    chevron_color: str = "primary",
) -> tuple[dropdown_main, nodes.container]:
    """Build a dropdown menu ready to be inlined."""

    # Configure the classes
    classes = [
        "sd-sphinx-override",
        "sd-dropdown",
        "sd-card",
        "sd-mb-3",
        "sd-mt-2",
    ]

    # Dropdown
    dropdown = dropdown_main(classes=classes)
    if is_open:
        dropdown["opened"] = True

    summary = dropdown_title(
        classes=[
            "sd-summary-title",
            "sd-card-header",
            "sd-bg-light",
            "sd-d-flex-row",
            "sd-align-major-justify",
            "sd-align-minor-center",
        ],
    )

    # Title
    title["classes"].extend(["sd-m-0", "sd-fw-semibold"])
    summary += title

    # Add the icon here
    chevron_wrapper = nodes.inline(classes=["sd-summary-icon"])
    if chevron_color:
        chevron_wrapper["classes"].append(f"sd-text-{chevron_color}")
    chevron_wrapper += nodes.raw("", get_octicon("chevron-down"), format="html")
    summary += chevron_wrapper

    dropdown += summary

    # Body
    body = nodes.container(
        is_div=True,
        classes=[
            "sd-summary-content",
            "sd-card-body",
            "sd-p-0",
            "sd-ml-3",
            "sd-mr-1",
        ],
    )
    dropdown += body

    return dropdown, body
