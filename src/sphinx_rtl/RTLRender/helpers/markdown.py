# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    04/10/2026
#
# Brief :   Convert a text stream formatted as markdown into a series of nodes.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes, utils
from myst_parser.parsers.docutils_ import Parser
from pathlib import Path
from sphinx.util import logging

# Configure the logger
logger = logging.getLogger(__name__)

# Configure the parser
md_parser = Parser()


def render_markdown(
    text: str, source_file: str = "", base_dir: Path = Path()
) -> list[nodes.Node]:
    """
    Convert a markdown string to a series of docutils nodes.

    The source file is used to enable absolute file resolution.
    """
    if not text or not text.strip():
        return [nodes.paragraph(text="-")]

    # Parse the document
    document = utils.new_document("")
    md_parser.parse(text.strip(), document)

    # Search for images or any relative path, and try to make them absolute
    count = 0
    for img in document.findall(nodes.image):
        raw_uri = img.get("uri", "")

        if raw_uri.startswith(("http://", "https://", "data:")):
            continue

        if source_file:
            resolved = (Path(source_file).parent / raw_uri).resolve()

            # Did we found something ?
            if resolved.is_file():

                # To ensure sphinx will operate, let's convert it to a relative path to the doc dir
                if base_dir is not None:
                    sphinx_path = resolved.relative_to(base_dir, walk_up=True)
                    img["uri"] = str(sphinx_path)
                    img["candidates"] = {"*": str(sphinx_path)}

                # Else try to use the default. Could fail in any way...
                else:
                    img["uri"] = str(resolved)
                    img["candidates"] = {"*": str(resolved)}

                count += 1

            else:
                logger.warning(
                    f"Image {raw_uri} could not be found on disk. Image could fail to load."
                )

                img.replace_self(
                    nodes.inline(
                        text=f"[Could not find image at {raw_uri}]",
                        classes=["sd-text-danger", "sd-fw-bold"],
                    )
                )

    if count > 0:
        logger.info(
            f"[INFO] Converted {count} link{"s" if count > 1 else ""} to absolute."
        )

    for p in document.findall(nodes.paragraph):
        p["classes"].append("sd-m-0")

    return document.children
