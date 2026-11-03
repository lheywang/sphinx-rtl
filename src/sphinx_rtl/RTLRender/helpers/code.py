# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    03/11/2026
#
# Brief :   Build a colored code example ready to be colored.
# ----------------------------------------------------------------------------

# Imports
from pathlib import Path
from docutils import nodes


def render_code(
    file: Path | str, language: str = "systemverilog"
) -> nodes.literal_block | nodes.error:
    """
    Render the provided file as a literal block, ready to be added.
    """

    # Convert the file to a Path in any cases.
    if isinstance(file, str):
        file = Path(file)

    # Does this file exists ?
    if not file.exists():
        return nodes.error("", nodes.paragraph(text=f"Could not find file : {file}"))

    # Fetch the contents
    content = file.read_text("utf-8")

    # Build the node
    node = nodes.literal_block(content, content)
    node["language"] = language
    node["classes"] += ["code", language, "custom-code-block"]

    return node


def render_raw_code(
    data: str, language: str = "systemverilog"
) -> nodes.literal_block | nodes.error:
    """
    Render the provided data as a literal block, ready to be added.
    """

    # Build the node
    node = nodes.literal_block(data, data)
    node["language"] = language
    node["classes"] += ["code", language, "custom-code-block"]

    return node
