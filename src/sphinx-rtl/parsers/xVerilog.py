# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Build the standard xVerilog (Verilog / SystemVerilog) parser.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast
import pyslang.syntax as syntax
import logging
from pathlib import Path

from ..models import Component, Parameter, Port, Enum, Import, Signal, Process
from .xParser import xParser

# Logger config
logger = logging.getLogger(__name__)


def to_text(cst_node) -> str:
    if cst_node is None:
        return ""
    # Instance neuve à chaque appel = buffer vierge
    return syntax.SyntaxPrinter().print(cst_node).str().strip()


class xVerilogParser(xParser):
    """
    Define the standard Verilog Parser model.
    Designed to be reused (can be openned only once and parse more than one file).
    """

    def __init__(self):
        """
        Init the xVerilog parser for different operations.
        """

        # No tools are needed, they're handled by the wheel !
        super().__init__()

    # ----------------------------------------------------------------------------
    # COMMENTS PARSERS
    # ----------------------------------------------------------------------------

    def fetch_comments(self, file: Path) -> list[tuple[int, str]]:
        """
        Fetch all the comments of the file, sorted by their lines.
        """
        # First, read all the lines:
        data = ""
        with open(file, "r") as f:
            data = f.read()

        # Doing this with a simple FSM
        state = "CODE"
        comments = []
        current_comment = []
        i = 0
        n = len(data)
        line = 1

        # Iterate over each character in the file.
        while i < n:
            char = data[i]
            next_char = data[i + 1] if i + 1 < n else ""

            if state == "CODE":
                if char == '"':
                    state = "STRING"
                elif char == "/" and next_char == "/":
                    state = "SINGLE_LINE_COMMENT"
                    i += 1
                elif char == "/" and next_char == "*":
                    state = "MULTI_LINE_COMMENT"
                    i += 1

            elif state == "STRING":
                if char == "\\" and next_char == '"':
                    i += 1
                elif char == '"':
                    state = "CODE"

            elif state == "SINGLE_LINE_COMMENT":
                if char == "\n":
                    comments.append(
                        (line, " ".join("".join(current_comment).split()).strip())
                    )
                    current_comment = []
                    state = "CODE"
                else:
                    current_comment.append(char)

            elif state == "MULTI_LINE_COMMENT":
                if char == "*" and next_char == "/":
                    comments.append(
                        (line, " ".join("".join(current_comment).split()).strip())
                    )
                    current_comment = []
                    state = "CODE"
                    i += 1
                elif char != "*":
                    current_comment.append(char)

            i += 1

            if char == "\n":
                line += 1

        if current_comment:
            comments.append("".join(current_comment))

        return comments

    # ----------------------------------------------------------------------------
    # GLOBAL PARSER
    # ----------------------------------------------------------------------------

    def parse(self, file: Path):
        """
        Parse the passed file as verilog, and output the built class.
        """

        # First get the file Infos
        infos = self.getFileInfo(file)

        # Extract the file comments
        comments = self.fetch_comments(file)

        # Extract the brief and detailed description
        brief, details = comments[0][1].split(".", 1)
        if not brief.endswith("."):
            brief += "."
        if not details.endswith("."):
            details += "."

        # Build the elements
        parameters: list[Parameter] = []
        ports: list[Port] = []
        enums: list[Enum] = []
        imports: list[Import] = []
        signals: list[Signal] = []
        processes: list[Process] = []

        # Run the tool to parse the file
        tree = syntax.SyntaxTree.fromFile(str(file))
        compilation = ast.Compilation()
        compilation.addSyntaxTree(tree)

        # Iterate over the different nodes :
        root = compilation.getRoot()
        for instance in root.topInstances:

            # List to track if the port name is already known, or not ?!?
            ports_names = []
            if isinstance(instance, ast.InstanceSymbol):
                for m in instance.body:
                    match m.kind:
                        case ast.SymbolKind.Parameter:
                            print(f"Parameter : {type(m).__name__}")

                        case ast.SymbolKind.TypeAlias:
                            print(f"Type Alias : {type(m).__name__}")

                        case (
                            ast.SymbolKind.WildcardImport
                            | ast.SymbolKind.ExplicitImport
                        ):
                            print(f"Import : {type(m).__name__}")

                        case ast.SymbolKind.Port:
                            header_node = m.syntax
                            print(
                                f"En-tête (m.syntax)           : {to_text(header_node)}"
                            )

                            # 2. La déclaration réelle avec le type dans le corps
                            internal = getattr(m, "internalSymbol", None)
                            if internal and internal.syntax:
                                # internal.syntax est le signal, son parent est la ligne complète (ex: input logic [XLEN-1:0] addr_in;)
                                body_decl_node = internal.syntax.parent
                                print(
                                    f"Corps (internalSymbol.parent) : {to_text(body_decl_node)}"
                                )

                        case ast.SymbolKind.Net | ast.SymbolKind.Variable:
                            print(f"Signal : {type(m).__name__}")

                        case ast.SymbolKind.ProceduralBlock:
                            print(f"Procedural : {type(m).__name__}")

        # Return the final component
        return Component(
            name="name",
            brief=brief,
            details=details,
            file=infos,
            parameters=parameters,
            ports=ports,
            enums=enums,
            imports=imports,
            signals=signals,
            process=processes,
        )
