# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   The common base for all of the language specific parsers
# ----------------------------------------------------------------------------

# Imports
import shutil
import git
import subprocess
import getpass
import datetime
import re

from git import Commit, GitCommandError
from sphinx.util import logging
from typing import TypeVar
from pathlib import Path

# Local imports
from ..models import FileInfo, Component, Element
from ..config import RenderConfig

# Import the IR subfunctions
from .ir import (
    infer_vendors,
    infer_polarity,
    infer_resets,
    infer_process,
    infer_clocks,
    infer_type,
)

# Configure logger
logger = logging.getLogger(__name__)

# Get our own custom type
T = TypeVar("T", bound=Element)


# class
class xParser:
    """
    Common core logic for the file
    """

    def __init__(self, tool=None):
        """
        Init the xVerilog parser for different operations.
        """

        # Ensure the tools are presents
        self.isToolAvailable = False
        if tool is not None:
            self.tool = shutil.which(tool)
            if self.tool is not None:
                logger.info(f"Found {tool} at {self.tool}")
                self.isToolAvailable = True
            else:
                logger.error(f"Cannot found a valid {tool} install.")
        else:
            self.tool = ""

    def runTool(self, args: str) -> str:
        """
        Run the tool in a safe subprocess. Return the raw command
        """
        # Build the command
        cmd = [self.tool]
        cmd.extend(args.split(" "))

        # Run the subprocess
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(
                f"Failed to run {self.tool} for with {args}.\n    Error is {res.stderr}"
            )

        return res.stdout

    def getFileInfo(self, file: Path) -> FileInfo:
        """
        Use the git history to look for the file history
        """

        # Get a fallback with the minimal set.
        fallback = FileInfo(
            name=file.name,
            path=str(file),
            creation_author="",
            edit_author=f"{getpass.getuser()}",
            creation_date="",  # Would match the date where you cloned the repo...
            edit_date=datetime.datetime.now().strftime("%m/%d/%Y %H:%M"),
            creation_hash="",
            edit_hash="",
            creation_tag="",
            edit_tag="",
            is_dirty=False,
            message="",
        )

        # First, open the repo. Ensure a fallback to ensure a working doc...
        try:
            repo = git.Repo(file, search_parent_directories=True)
        except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):  # type: ignore
            logger.warning(
                "Could not find a valid git repo. Using the filesystem fallback."
            )
            return fallback

        obj = file.resolve()

        # Fetch the relative path
        try:
            rel_obj = obj.relative_to(str(repo.working_tree_dir))
        except ValueError:
            return fallback

        commits: list[Commit] = list(repo.iter_commits(paths=str(rel_obj)))
        if not commits:
            return fallback

        # Fetch the last commits
        last_commit = commits[0]
        first_commit = commits[-1]

        # Fetch the tags
        def find_first_tag_containing(commit_sha: str) -> str | None:
            """Find the first tag (to the future) that contain the target commit."""
            try:
                raw = repo.git.describe("--tags", "--contains", commit_sha)
                return re.split(r"[\^~]", raw)[0]
            except GitCommandError:
                return None

        # Fetch them
        last_tag = find_first_tag_containing(last_commit.hexsha)
        first_tag = find_first_tag_containing(first_commit.hexsha)

        # Safety to ensure at least a tag is present
        if last_tag is None:
            for c in commits[1:]:
                t = find_first_tag_containing(c.hexsha)
                if t:
                    last_tag = f"{t} (+ unreleased)"
                    break
            else:
                last_tag = "unreleased"

        # Check if the file has been modified since
        is_dirty = bool(repo.index.diff(None, paths=[str(rel_obj)])) or bool(
            repo.head.commit.diff(None, paths=[str(rel_obj)])
        )

        # Build the info structure
        return FileInfo(
            name=file.name,
            path=str(file),
            creation_author=f"{first_commit.author.name} <{first_commit.author.email}>",
            edit_author=f"{last_commit.author.name} <{last_commit.author.email}>",
            creation_date=first_commit.committed_datetime.strftime("%m/%d/%Y %H:%M"),
            edit_date=last_commit.committed_datetime.strftime("%m/%d/%Y %H:%M"),
            creation_hash=first_commit.hexsha[:12],
            edit_hash=last_commit.hexsha[:12],
            creation_tag=str(first_tag),
            edit_tag=str(last_tag),
            is_dirty=is_dirty,
            message=(
                last_commit.message.decode("utf8")
                if type(last_commit.message) == bytes
                else str(last_commit.message)
            ).strip(),
        )

    def _findLines(self, line: int) -> tuple[int, int]:
        """
        Return the feasible lines for the passed line
        """
        return (line, line - 1)

    def _linkElementComment(
        self, targets: list[T], comments: dict, available: set[int]
    ) -> tuple[tuple[int, int], set[int]]:
        """
        Link the comments for a specific type of nodes in the IR
        """
        count = 0
        missing = 0
        for target in targets:

            current_line, previous_line = self._findLines(target.line)
            if current_line in available:
                target.description = comments[current_line]
                available.remove(current_line)
                count += 1
            elif previous_line in available:
                target.description = comments[previous_line]
                available.remove(previous_line)
                count += 1
            else:
                missing += 1

        return (count, missing), available

    def linkComments(
        self, component: Component, comments: dict
    ) -> tuple[int, int, int, Component]:
        """
        Link the comments as parsed to the component
        """
        # Comment count linker
        count: int = 0
        misses: int = 0

        # Fetch the available comments
        available_comments = set(comments.keys())

        # Link them.
        # The order is designed to go from the most important (ports, parameters) to the least (signals ...)
        link_targets = [
            component.ports,
            component.parameters,
            component.enums,
            component.process,
            component.modules,
            [param for mod in component.modules for param in mod.params],
            component.imports,
            component.interfaces,
            [param for mod in component.interfaces for param in mod.parameters],
            [signal for mod in component.interfaces for signal in mod.signals],
            [port for mod in component.interfaces for port in mod.ports],
            [modport for mod in component.interfaces for modport in mod.modports],
            component.signals,
            component.functions,
            [arg for mod in component.functions for arg in mod.func_inputs],
            [arg for mod in component.functions for arg in mod.func_outputs],
            component.structures,
            [signal for mod in component.structures for signal in mod.signals],
        ]

        for target in link_targets:
            stats, available_comments = self._linkElementComment(
                target, comments, available_comments
            )
            count += stats[0]
            misses += stats[1]

        remaining = len(available_comments)
        # Remaining comments
        return count, misses, remaining, component

    def fetchFlags(self, component: Component, src: str) -> Component:
        """
        Fetch the different flags that are available, and parse the comments.
        """
        return component

    def inferElements(self, component: Component) -> Component:
        """
        Infer, as selected by the config file the different elements on the IR.
        """

        cfg: RenderConfig = component.render

        # ------------------------------
        # INFER IOs
        # ------------------------------
        if cfg.inferIOs:
            component = infer_process(component)

            # ------------------------------
            # INFER CLOCKS
            # ------------------------------
            if cfg.inferClocks:
                component = infer_clocks(component)

            # ------------------------------
            # INFER RESETS
            # ------------------------------
            if cfg.inferResets:
                component = infer_resets(component)

        else:
            if cfg.inferClocks:
                logger.warning(
                    "Could not infer clocks. IO inferring is required for this feature to be available."
                )
            if cfg.inferResets:
                logger.warning(
                    "Could not infer resets. IO inferring is required for this feature to be available."
                )

        # ------------------------------
        # INFER POLARITY
        # ------------------------------
        if cfg.inferPolarity:
            component = infer_polarity(component)

        # ------------------------------
        # INFER COMPONENT TYPE
        # ------------------------------
        if cfg.inferType:
            component = infer_type(component)

        # ------------------------------
        # INFER MODULE RESOLUTION
        # ------------------------------
        if cfg.resolution:
            pass

        # ------------------------------
        # INFER VENDORS
        # ------------------------------
        if cfg.inferVendor:
            component = infer_vendors(component)

        # Return
        return component
