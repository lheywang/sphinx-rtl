# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    05/10/2026
#
# Brief :   Build a reference with the matching parameters.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes, utils
from docutils.nodes import make_id


def render_ref(name: str, comp: str = "none", name_type: str = "none") -> nodes.target:
    """
    Declare a reference to the passed name. References are built on the following format :

    {comp}-{name_type}-{name}

    where each element is passed. This ensure both an easy way to remember the ref ? Where ? What ? Who ?
    and a uniqueness of them, as per the specifications of any languages (there could not be two port with the same name).
    """
    target_name = f"{comp}-{name_type}-{name}"

    return nodes.target("", "", ids=[make_id(target_name)], names=[target_name])
