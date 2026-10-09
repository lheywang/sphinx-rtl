# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/10/2026
#
# Brief :   Build a reference with the matching parameters.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx import addnodes
from docutils.nodes import make_id


def make_ref_id(name: str, comp: str, name_type: str):
    """
    Build the reference name
    """
    return f"{comp}-{name_type}-{name}"


def render_ref(
    name: str,
    comp: str = "none",
    name_type: str = "none",
    refs: list[dict] = [],
) -> nodes.target:
    """
    Declare a reference to the passed name. References are built on the following format :

    {comp}-{name_type}-{name}

    where each element is passed. This ensure both an easy way to remember the ref ? Where ? What ? Who ?
    and a uniqueness of them, as per the specifications of any languages (there could not be two port with the same name).

    The refs element may be used to keep track of global list of references across the RTLDomain.
    """

    # Build the id
    target_name = make_ref_id(name, comp, name_type)

    # Add the id to the internal bank
    refs.append(
        {
            "target_id": target_name,
            "name": name,
            "comp": comp,
            "type": name_type,
        }
    )

    return nodes.target("", "", ids=[make_id(target_name)], names=[target_name])


def use_ref(
    name: str,
    comp: str = "none",
    name_type: str = "none",
    label: (
        nodes.Text
        | nodes.literal
        | nodes.inline
        | list[nodes.Node]
        | nodes.literal
        | nodes.paragraph
    ) = nodes.paragraph(),
    as_literal: bool = True,
):
    """
    Add a pending xref into the document.
    """

    # Fetch the reference name
    norm = make_id(make_ref_id(name, comp, name_type))

    pxref = addnodes.pending_xref(
        "", refdomain="rtl", reftype=name_type, reftarget=norm, refwarn=True
    )
    pxref["classes"].append("sd-text-decoration-none")

    # Add the node type
    pxref += label

    return pxref
