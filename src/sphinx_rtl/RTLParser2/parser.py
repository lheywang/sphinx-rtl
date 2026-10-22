# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    19/10/2026
#
# Brief :   Define the new RTLParser component, based on tree-sitter plugin.
#           Faster, easier to use and a cleaner approach.
# ----------------------------------------------------------------------------

# Imports
from sphinx.util import logging
from sphinx._cli.util.colour import blue
from pathlib import Path
from tree_sitter import Parser, QueryCursor

from .registry import SpecificationRegistry
from .languages import VHDLSpecification, SystemverilogSpecification
from .tracker import EntityTracker, AddingPolicy
from .linker import link_comments

from sphinx_rtl.models import Component, Comment, ALL_MODELS

# Configure the global parser and add the different specifications to it
registry = SpecificationRegistry()
registry.add_specification(VHDLSpecification())
registry.add_specification(SystemverilogSpecification())

# Configure the logger
logger = logging.getLogger(__name__)


# Build the global class for it
class RTLParser2:
    """
    The parsing class. This version 2 is actually about 5x faster compared to the original version (<= v0.5.0),
    while maintaining the same level of features.
    """

    def __init__(self) -> None:
        """
        Init the parser class.
        """

    def parse(self, file: Path) -> dict[str, Component]:
        """
        Parse the passed file into a list of components.
        """

        # First, fetch the matching Specification and the Parser
        self.specification = registry.get_specification(file)
        logger.info(blue(f"[INFO] Using {self.specification.name} for the file."))

        # Did the file is defined as ts ?
        if self.specification.ts_lang is not None:
            self.parser = Parser(self.specification.ts_lang)
            return self._parse_as_ts(file)

        # Else, call the raw parser
        return self._parse_as_std(file)

    def _parse_as_ts(self, file: Path) -> dict[str, Component]:
        """
        Parse the file following a tree-sitter based language.
        """

        # First, read and parse the file
        code: bytes = file.read_bytes()
        tree = self.parser.parse(code)

        # Init the tracker
        tracker = EntityTracker()
        comments: list[Comment] = []

        # Run the first query to discover the elements
        if (
            self.specification.ts_explore_query != ""
            and self.specification.ts_top_name is not None
        ):
            explore_cursor = QueryCursor(
                self.specification.ts_queries[self.specification.ts_explore_query]
            )
            for index, match in explore_cursor.matches(tree.root_node):
                tracker.add_entity(match, file, code, self.specification.ts_top_name)
        else:
            logger.error(
                f"Specification {self.specification.name} did not define an explore Query or the ts_top_name. Could not allocate memory for the parsing. Exiting."
            )
            return {}

        # Using queries, we could fetch all elements directly
        logger.info(
            blue(
                f"[INFO] Executing {len(self.specification.ts_queries)} queries to the AST."
            )
        )
        for name, query in self.specification.ts_queries.items():

            # Ignore the exploration query
            if name == self.specification.ts_explore_query:
                continue

            # Perform the request over the passed tree
            cursor = QueryCursor(query)

            # Iterate over the list of results
            for index, match in cursor.matches(tree.root_node):
                result = self.specification.ts_transformers[name](index, match, code)

                # Place all of that under a list
                results = []
                if isinstance(
                    result,
                    ALL_MODELS | Comment,
                ):
                    results = [result]
                elif type(result) is list:
                    results = result

                for res in results:
                    # Is there something for us ?
                    if res is None:
                        continue
                    elif isinstance(res, Comment):
                        comments.append(res)
                    elif isinstance(res, ALL_MODELS):
                        tracker.add_to_entity(res, AddingPolicy.ADD_TO_ALL)

        # Do we have a callback to execute ?
        if self.specification.comment_transformer is not None:
            logger.info(blue(f"[INFO] Executing the comment transformer provided"))
            comments = self.specification.comment_transformer(comments)

        # Finally, link the comments with the elements
        link_comments(comments, tracker.components)

        return tracker.components

    def _parse_as_std(self, file: Path) -> dict[str, Component]:
        """
        Parse the file following a raw approach.
        """

        # Is there anything to call ?
        if self.specification.std_parser is not None:
            return self.specification.std_parser(file)

        # Else return an empty list
        logger.error(
            f"File {file.name} was not parsed because std_parser function is not defined."
        )
        return {}
