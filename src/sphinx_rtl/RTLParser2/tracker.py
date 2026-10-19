# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Track the components defined within a file and handle the
#           properties of these components.
# ----------------------------------------------------------------------------

# Import
import sys

from tree_sitter import Node
from pathlib import Path
from sphinx.util import logging
from enum import Enum as classEnum

from sphinx_rtl.models import Component
from sphinx_rtl.RTLParser2.languages import get_text
from sphinx_rtl.models import (
    Component,
    Port,
    Enum,
    Parameter,
    Structure,
    Import,
    Signal,
    Process,
    Assignment,
    Module,
    Function,
    Interface,
)

from .utils import getFileInfo

# Configure the logger
logger = logging.getLogger(__name__)


# Define the policy enum
class AddingPolicy(classEnum):
    """
    Define what we need to do with unbound elements.

    Four possibles choices :
        - ADD_TO_ALL : Add the element to all register elements. Useful for libraries and other things like that.
        - ADD_TO_FIRST : Add to the first element on the file.
        - ADD_TO_LAST : Add to the last element on the file
        - DO_NOT_ADD : Don't add and emit a warning
        - DO_NOT_ADD_QUIET : Don't add and exit silently
    """

    ADD_TO_ALL = 0
    ADD_TO_FIRST = 1
    ADD_TO_LAST = 2
    DO_NOT_ADD = 3
    DO_NOT_ADD_QUIET = 4


class EntityTracker:
    """
    Handle the components instantiations within a file, and handle the
    insertion of elements into them.
    """

    def __init__(self, max_lines: int = sys.maxsize) -> None:
        """
        Initialize the component registry.
        """
        self.end = max_lines
        self.components: dict[str, Component] = {}
        self.scopes: list[dict] = []

    def add_entity(self, nodes: dict[str, list[Node]], file: Path, code: bytes) -> None:
        """
        Add an entity into the register. Will reuse them later to
        append properties if needed.
        """

        # Fetch the entity name
        name = get_text(nodes["entity.name"][0], code)

        start_line = nodes["entity.node"][0].end_point[0]

        # Update the register
        if self.scopes and self.scopes[-1]["end"] == self.end:
            self.scopes[-1]["end"] = max(self.scopes[-1]["start"], start_line - 1)
        self.scopes.append({"name": name, "start": start_line, "end": self.end})

        # Get file infos
        infos = getFileInfo(file)

        # Build the component
        self.components[name] = Component(infos, name=name)

    def add_to_entity(
        self,
        element: (
            Port
            | Enum
            | Parameter
            | Structure
            | Import
            | Signal
            | Process
            | Assignment
            | Module
            | Function
            | Interface
        ),
        policy: AddingPolicy,
    ) -> None:
        """
        Add a built object into the right entity.

        Note : the policy is applied in case the element does NOT match anything.
        """

        # First, fetch the target entity
        target = self.resolve(element.line)

        if target is not None:

            match element:

                case Port():
                    target.ports.append(element)
                case Parameter():
                    target.parameters.append(element)
                case Enum():
                    target.enums.append(element)
                case Import():
                    target.imports.append(element)
                case Process():
                    target.process.append(element)
                case Signal():
                    target.signals.append(element)
                case Interface():
                    target.interfaces.append(element)
                case Module():
                    target.modules.append(element)
                case Function():
                    target.functions.append(element)
                case Structure():
                    target.structures.append(element)
                case Assignment():
                    target.assigns.append(element)
                case _:
                    logger.warning(
                        f"Attempted to add {type(element)} to a Component. This operation is not permitted and was ignored."
                    )

            return

        # Else, we need to handle the policy
        match policy:

            case AddingPolicy.ADD_TO_ALL:
                for scope in self.scopes:
                    element.line = scope["start"]
                    self.add_to_entity(element, AddingPolicy.DO_NOT_ADD)

            case AddingPolicy.ADD_TO_FIRST:
                element.line = 0
                self.add_to_entity(element, AddingPolicy.DO_NOT_ADD)

            case AddingPolicy.ADD_TO_LAST:
                element.line = self.end
                self.add_to_entity(element, AddingPolicy.DO_NOT_ADD)

            case AddingPolicy.DO_NOT_ADD:
                logger.error(
                    f"Could not find a matching entity in the register to add the current {type(element)}. This operation will be ignored."
                )

            case AddingPolicy.DO_NOT_ADD_QUIET:
                pass

        return

    def resolve(self, line: int) -> Component | None:
        """
        Return the entity where the element must be added.
        """

        # Get the entity
        target = ""
        for scope in self.scopes:
            if scope["start"] <= line <= scope["end"]:
                target = scope["name"]
                break

        # Get the component
        if target != "":
            return self.components[target]
        return None
