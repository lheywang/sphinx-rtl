# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   The common base for all of the language specific parsers
# ----------------------------------------------------------------------------

# Imports
import shutil
import logging
import git

from pathlib import Path

# Local imports
from ..models import FileInfo

# Configure logger
logger = logging.getLogger(__name__)


# class
class xParser:
    """
    Common core logic for the file
    """

    def __init__(self, tool):
        """
        Init the xVerilog parser for different operations.
        """

        # Ensure the tools are presents
        self.isToolAvailable = False
        self.tool = shutil.which(tool)
        if self.tool is not None:
            logger.info(f"Found {tool} at {self.tool}")
            self.isToolAvailable = True
        else:
            logger.error(f"Cannot found a valid {tool} install.")

    def getFileInfo(self, file: Path) -> FileInfo:
        """
        Use the git history to look for the file history
        """

        # First, open the repo. Ensure a fallback to ensure a working doc...
        try:
            repo = git.Repo(file, search_parent_directories=True)
        except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
            return FileInfo(
                file.name,
                str(file),
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                False,
                "none",
            )

        obj = file.resolve()

        # Fetch the relative path
        try:
            rel_obj = obj.relative_to(str(repo.working_tree_dir))
        except ValueError:
            return FileInfo(
                file.name,
                str(file),
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                False,
                "none",
            )

        commits = list(repo.iter_commits(paths=str(rel_obj)))
        if not commits:
            return FileInfo(
                file.name,
                str(file),
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                "unknown",
                False,
                "none",
            )

        # Fetch the last commits
        last_commit = commits[0]
        first_commit = commits[-1]

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
            is_dirty=is_dirty,
            message=(
                last_commit.message.decode("utf8")
                if type(last_commit.message) == bytes
                else str(last_commit.message)
            ).strip(),
        )
