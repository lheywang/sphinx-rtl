# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    03/11/2026
#
# Brief :   Render tabs that may be synchronized together to render elements.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx_design.tabs import sd_tab_label


def render_tabs(titles, group="rtl"):

    # Building the top level container.
    tab_set = nodes.container(
        is_div=True, design_component="tab-set", classes=["sd-tab-set"]
    )
    tab_set["sync_group"] = group
    contents = {}

    # Build the container for each elements.
    for title in titles:

        # Create the container
        item = nodes.container(is_div=True, design_component="tab-item")
        label = sd_tab_label(
            "", "", nodes.inline(title, title), classes=["sd-tab-label"]
        )
        label["sync_id"] = title
        label["sync_group"] = group

        # Create the user accessible content
        content = nodes.container(
            is_div=True, design_component="tab-content", classes=["sd-tab-content"]
        )

        # Add them to their parents
        item += label
        item += content
        tab_set += item

        # Update the output dict.
        contents[title] = content

    return tab_set, contents
