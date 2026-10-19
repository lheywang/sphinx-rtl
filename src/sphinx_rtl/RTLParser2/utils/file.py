# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the fileInfo functions.
# ----------------------------------------------------------------------------

# Imports
import getpass
import datetime
import git
import re

from pathlib import Path
from sphinx.util import logging
from git import Commit, GitCommandError

from sphinx_rtl.models import FileInfo

# Configure the logger
logger = logging.getLogger(__name__)


# Function
def getFileInfo(file: Path) -> FileInfo:
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
