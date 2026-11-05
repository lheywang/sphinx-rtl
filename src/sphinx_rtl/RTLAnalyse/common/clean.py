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

logger = logging.getLogger(__name__)


def clean(component: Component) -> Component:
    """
    Remove all empty strings elements !
    """

    def _cleaned(elements: list) -> list:
        return [x for x in elements if x]

    # Clean up cfg
    component.config.warning = _cleaned(component.config.warning)
    component.config.notes = _cleaned(component.config.notes)
    component.config.constraints = _cleaned(component.config.constraints)
    component.config.compliance = _cleaned(component.config.compliance)
    component.config.target = _cleaned(component.config.target)
    component.config.tool = _cleaned(component.config.tool)
    component.config.sim = _cleaned(component.config.sim)
    component.config.license = _cleaned(component.config.license)
    component.config.tags = _cleaned(component.config.tags)

    return component
