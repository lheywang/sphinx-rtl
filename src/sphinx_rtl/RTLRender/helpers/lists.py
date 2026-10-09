# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    30/09/2026
#
# Brief :   Build a badges from the provided data
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes


def render_bullet_list(
    elements: list[
        nodes.Text
        | nodes.literal
        | nodes.inline
        | list[nodes.Node]
        | nodes.literal
        | nodes.paragraph
    ],
) -> nodes.bullet_list:
    """
    Build a list from the passed elements.
    """

    blist = nodes.bullet_list(classes=["sd-list-unstyled", "sd-m-3"])

    for element in elements:

        # Build an item
        item = nodes.list_item()

        # If not a paragraph, add it
        if type(element) is not nodes.paragraph:
            p = nodes.paragraph()
            p += element

            # Add to the item
            item += p

        # Else, add it directly
        else:
            item += element

        # Add to the list
        blist += item

    return blist


def render_def_list(
    elements: list[
        nodes.Text
        | nodes.literal
        | nodes.inline
        | list[nodes.Node]
        | nodes.literal
        | nodes.term
    ],
    definitions: list[
        nodes.Text
        | nodes.literal
        | nodes.inline
        | list[nodes.Node]
        | nodes.literal
        | nodes.definition
    ],
) -> nodes.definition_list:
    """
    Render a definition list
    """

    dlist = nodes.definition_list(classes=["sd-m-3"])

    for element, definition in zip(elements, definitions):
        item = nodes.definition_list_item()

        # Do we have a term ? If not, build it
        if type(element) is not nodes.term:
            term = nodes.term()
            term += element

            item += term

        # Else we already have a term, add it directly
        else:
            item += element

        # Add the definition

        # Do we have a paragraph ? Else build it
        if type(definition) is not nodes.definition:
            d = nodes.definition(
                classes=["sd-ms-4", "sd-pb-2", "sd-mb-2", "border-bottom"]
            )
            d += definition
            item += d

        # Yes, add it directly
        else:
            item += definition

        # Add the element to the list
        dlist += item

    # Return the list
    return dlist
