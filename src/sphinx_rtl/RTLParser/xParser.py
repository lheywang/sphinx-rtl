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

from dataclasses import dataclass, fields
from typing import Any, get_args, get_origin
from collections import defaultdict
from git import Commit, GitCommandError
from sphinx.util import logging
from typing import TypeVar
from pathlib import Path

# Local imports
from sphinx_rtl.models import FileInfo, Component, Element
from sphinx_rtl.config import RenderConfig

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
                logger.info(f"[INFO] Found {tool} at {self.tool}")
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
            repo_path="",
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
            repo_path=str(Path(repo.git_dir).parent),
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

    def cleanComment(self, src: str) -> str:
        """
        Clean the comment string, regardless of the language.
        """
        return re.sub(r"^\s*(?:\/\*+|\*+|\/\/|--)\s?", "", src)

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
                target.description = comments[current_line].strip()
                available.remove(current_line)
                count += 1
            elif previous_line in available:
                target.description = comments[previous_line].strip()
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

        RE_TAG_LINE = re.compile(r"^.*@([a-zA-Z_]\w*)(?:\s+(.*))?$")

        # Allocate variables for later
        desc_lines: list[str] = []
        raw_tags: dict[str, list[str]] = defaultdict(list)
        current_tag: str | None = None

        # Fetch all the things that could look like a flag
        for line in src.splitlines():
            cleaned = re.sub(r"^\s*(?:\/\*+|\*+|\/\/|--)\s?", "", line).rstrip()

            matched = RE_TAG_LINE.match(cleaned)
            if matched:
                name = matched.group(1)
                val = matched.group(2).strip() if matched.group(2) else ""
                raw_tags[name].append(val)
                current_tag = name
            elif current_tag is not None and cleaned.startswith(" "):
                raw_tags[current_tag][-1] += " " + cleaned.strip()
            else:
                current_tag = None
                if cleaned or desc_lines:
                    desc_lines.append(cleaned)

        # Dispatch the names of the config classes into a dict.
        field_dispatch: dict[str, tuple[Any, Any]] = {}
        for obj in (component.config, component.render):
            for field in fields(obj):
                field_dispatch[field.name.lower().replace("_", "")] = (obj, field)

        # Injection du type dans la classe de config:
        count = 0
        missed = 0
        for raw_name, values in raw_tags.items():
            name = raw_name.lower().replace("_", "")
            negated = None

            # Support mistyped elements that may start with no
            if (
                name.startswith("no")
                and name[2:] in field_dispatch
                and field_dispatch[name[2:]][1].type is bool
            ):
                name = name[2:]
                negated = True

            if name in field_dispatch:
                obj, field = field_dispatch[name]
                f_type = field.type
                val = values[-1]

                # Is this a boolean ?
                if f_type is bool:
                    if negated:
                        bit = False
                    elif val:
                        bit = val.lower() not in ("false", "0", "no", "off")
                    else:
                        bit = True

                    setattr(obj, field.name, bit)

                # Is that a list (or depends from a list)
                elif get_origin(f_type) is list or f_type is list:
                    current_list = getattr(obj, field.name)
                    current_list.extend(v for v in values if v)

                # Is that a dict ?
                elif get_origin(f_type) is dict or f_type is dict:
                    target_dict = getattr(obj, field.name)
                    for entry in values:
                        parts = entry.split(maxsplit=1)
                        if len(parts) == 2:
                            target_dict[parts[0]] = parts[1]
                        elif len(parts) == 1:
                            target_dict["default"] = parts[0]

                # Is that a string ?
                else:
                    setattr(obj, field.name, val)

                count += 1

            else:
                for v in values:
                    tag_repr = f"@{name} {v}".strip()
                    component.config.tags.append(tag_repr)

                missed += 1

            while desc_lines and not desc_lines[-1].strip():
                desc_lines.pop()

        if count > 0:
            logger.info(
                f"[INFO] Found {count} flag{"s" if count > 1 else ""} and configured them."
            )
        elif missed > 0:
            logger.warning(
                f"Found {missed} flag{"s" if missed > 1 else ""} that are unknown, and placed into the flags config."
            )

        # Update the component elements
        RE_SENTENCE_SPLIT = re.compile(r"\.(?:\s+|$)")

        comment = "\n".join(desc_lines)
        raw = RE_SENTENCE_SPLIT.split(comment, maxsplit=1)

        component.brief = raw[0].strip()
        component.details = raw[1].strip() if len(raw) > 1 else ""

        return component
