# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    02/11/2026
#
# Brief :   Clean the messages from all structures.
# ----------------------------------------------------------------------------

# Imports
from sphinx_rtl.models import Component

# Configure logger
from sphinx.util import logging
from sphinx._cli.util.colour import blue

from sphinx_rtl.models import Import

logger = logging.getLogger(__name__)


def bind_libraries(component: Component) -> Component:
    """
    Combine libraries that share an element into one "big" library.
    """

    libs: dict[str, Import] = {}

    # Iterate over libs. If we do know it, add it to the import, otherwise let's create a new one !
    for imp in component.imports:

        if imp.library in libs:
            libs[imp.library].element.extend(imp.element)
        else:
            libs[imp.library] = imp

    # Replace the output
    component.imports = list(libs.values())

    return component
