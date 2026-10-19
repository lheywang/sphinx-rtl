# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the language registry, to be used over each instances
#           of parsers.
# ----------------------------------------------------------------------------

# Imports
from pathlib import Path
from sphinx.util import logging
from sphinx._cli.util.colour import darkgray

from sphinx_rtl.RTLParser2.languages import LanguageSpec

# Configure the logger
logger = logging.getLogger(__name__)


# Class
class SpecificationRegistry:
    """
    Hold the registry of languages, and propose the export function to be called when
    a parser thread is invoked.

    Shared across threads, therefore must be readonly.
    """

    def __init__(self) -> None:
        """
        Init the class, with an empty specification.
        """

        self.specifications: dict[str, LanguageSpec] = {}

    def add_specification(self, specification: LanguageSpec):
        """
        Add a specification within the internal bank. Will be called
        later.
        """

        # Register for all the different extensions available.
        # Let's normalize it to ensure reliability.
        for extension in specification.extensions:
            self.specifications[extension.lower()] = specification

        # Logs
        logger.info(
            darkgray(
                f"[INFO] Added {len(specification.extensions)} extension{"s" if len(specification.extensions) > 1 else ""} from {specification.name} into the registry."
            )
        )

    def get_specification(self, extension: Path) -> LanguageSpec:
        """
        Return the correct specification to be used for this language.
        """

        # Fetch the parser
        target_key = extension.suffix.removeprefix(".")
        target = self.specifications.get(target_key)
        if target is not None:
            return target
        else:
            logger.error(
                f"Could not find a suitable LanguageSpec for {extension}. Did you added it ?"
            )
            return LanguageSpec("error")

    def get_all_extension(self) -> list[str]:
        """
        Return all known extensions that could therefore be searched for.
        """

        ext: list[str] = []
        for spec in self.specifications.values():
            ext.extend(spec.extensions)

        return ext
