# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Build the standard xVerilog (Verilog / SystemVerilog) parser.
# ----------------------------------------------------------------------------

# Imports
import pyslang.ast as ast
import pyslang.syntax as syntax
from sphinx.util import logging
from pyslang import SourceManager
from pathlib import Path

from ..models import (
    Component,
    Parameter,
    Port,
    Enum,
    Import,
    Signal,
    Process,
    Assignment,
    Interface,
    Module,
    Element,
)
from .xParser import xParser
from .xVerilogFunctions import (
    build_signal,
    build_process,
    build_port,
    build_interfacePort,
    build_parameter,
    build_interface,
    build_enum,
    build_assignment,
    build_module,
    extract_imports,
    build_function,
    build_struct,
    build_generate,
)

# Configure the logger
logger = logging.getLogger(__name__)


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

        # Init the elements to induce the memory effect between the calls required by the Verilog specification.
        self.port = Port()
        self.ports_names: list[str] = []

        # Append the source manager :
        self.sm: SourceManager = SourceManager()

        # Get some stats
        self.ignored = 0

    # ----------------------------------------------------------------------------
    # COMMENTS PARSERS
    # ----------------------------------------------------------------------------

    def fetch_comments(self, file: Path) -> dict:
        """
        Fetch all the comments of the file, sorted by their lines.
        """
        # First, read all the lines:
        data = ""
        with open(file, "r") as f:
            data = f.read()

        # Doing this with a simple FSM
        state = "CODE"
        comments = dict()
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
                current_comment.append(char)
                if char == "\n" and not next_char == "/":
                    current_comment.append(char)
                    comments[line] = "".join("".join(current_comment))
                    current_comment = []
                    state = "CODE"

            elif state == "MULTI_LINE_COMMENT":
                current_comment.append(char)
                if char == "*" and next_char == "/":
                    comments[line] = "".join("".join(current_comment))
                    current_comment = []
                    state = "CODE"
                    i += 1

            i += 1

            if char == "\n":
                line += 1

        if current_comment:
            comments[line] = "".join(current_comment)

        return comments

    def get_line(self, node) -> int:
        """
        Return the line (or -1) of the specified node
        """
        # Add the line
        source = self.sm.getLineNumber(node)
        if source > 0:
            return source
        else:
            return -1

    # ----------------------------------------------------------------------------
    # GLOBAL PARSER
    # ----------------------------------------------------------------------------

    def populate_component(
        self, comp: Component, scope: ast.Scope, is_package: bool = False
    ) -> None:
        """
        Populate a component from the right sources.
        """

        for m in scope:

            match m.kind:

                # PARAMETER
                case ast.SymbolKind.Parameter:
                    comp.parameters.append(
                        build_parameter(m, self.get_line(m.location))  # type: ignore
                    )

                # TYPE ALIAS
                case ast.SymbolKind.TypeAlias:
                    if m.isEnum:  # type: ignore
                        comp.enums.append(build_enum(m, self.get_line(m.location)))  # type: ignore
                    elif m.isStruct:  # type: ignore
                        comp.structures.append(build_struct(m, self.get_line(m.location), self.sm))  # type: ignore

                # PORTS
                case ast.SymbolKind.Port:
                    # Add the port here
                    self.ports_names.append(m.name)
                    port = build_port(self.port, m, self.get_line(m.location))  # type: ignore
                    comp.ports.append(port)
                    self.port = port

                # INTERFACE PORT
                case ast.SymbolKind.InterfacePort:
                    self.ports_names.append(m.name)
                    port = build_interfacePort(self.port, m, self.get_line(m.location))  # type: ignore
                    comp.ports.append(port)
                    self.port = port

                # SYMBOL / NET
                case ast.SymbolKind.Net | ast.SymbolKind.Variable:
                    if m.name not in self.ports_names:
                        comp.signals.append(build_signal(m, self.get_line(m.location)))  # type: ignore

                # PROCESS
                case ast.SymbolKind.ProceduralBlock:
                    comp.process.append(build_process(m, self.get_line(m.location)))  # type: ignore

                # ASSIGN
                case ast.SymbolKind.ContinuousAssign:
                    comp.assigns.append(build_assignment(m, self.get_line(m.location)))  # type: ignore

                # INSTANCE
                case ast.SymbolKind.Instance:
                    comp.interfaces.append(
                        build_interface(m, self.get_line(m.location), self.sm)  # type: ignore
                    )

                # FUNCTIONS
                case ast.SymbolKind.Subroutine:
                    comp.functions.append(build_function(m, self.get_line(m.location)))  # type: ignore

                # INSTANCE MODULE
                case ast.SymbolKind.UninstantiatedDef:
                    comp.modules.append(
                        build_module(m, self.get_line(m.location), self.sm)
                    )

                # GENERATE
                case ast.SymbolKind.GenerateBlock | ast.SymbolKind.GenerateBlockArray:
                    comp.modules.extend(build_generate(m, self.get_line(m.location), self.sm))  # type: ignore

                # We don't care about these, they're proxies to enums and other stuff like that
                case (
                    ast.SymbolKind.TransparentMember
                    | ast.SymbolKind.Genvar
                    | ast.SymbolKind.EmptyMember
                ):
                    self.ignored += 1

                case _:
                    logger.warning(f"[WARN] Unknown element ({m.kind}) : {str(m.name)}")

        # Update the package type.
        if is_package:
            comp.comp_type = "package"
            comp.config.isPackage = True

    def parse(self, file: Path):
        """
        Parse the passed file as verilog, and output the built class.
        """

        # First get the file Infos
        infos = self.getFileInfo(file)
        comp = Component(file=infos)
        comp.name = file.name.rsplit(".", 1)[0]

        # Extract the file comments
        comments = self.fetch_comments(file)

        # Extract the brief and detailed description
        # Then delete it to ensure it won't be reused.
        if len(comments.keys()) > 0:
            comp = self.fetchFlags(comp, comments[list(comments.keys())[0]])

        # Run the tool to parse the file
        tree = syntax.SyntaxTree.fromFile(str(file))
        compilation = ast.Compilation()
        compilation.addSyntaxTree(tree)

        interfaces = []
        modules = []
        for member in tree.root.members:  # type: ignore
            if hasattr(member, "header") and hasattr(member.header, "name"):
                name = member.header.name.valueText
                if member.kind == syntax.SyntaxKind.InterfaceDeclaration:
                    interfaces.append(name)
                elif member.kind == syntax.SyntaxKind.ModuleDeclaration:
                    modules.append(name)

        # If nothing is found, perhaps we need to add a small empty module ?
        if len(interfaces) > 0 and len(modules) == 0:
            stub = "\n".join(
                [
                    f"module __doc_top_{iface}; {iface} __inst(); endmodule"
                    for iface in interfaces
                ]
            )
            stub_tree: syntax.SyntaxTree = syntax.SyntaxTree.fromText(stub)
            compilation.addSyntaxTree(stub_tree)

        # Fetch the compilation root
        root: ast.RootSymbol = compilation.getRoot()
        self.sm: SourceManager = compilation.sourceManager

        # Extract the different packages
        packages = [x for x in compilation.getPackages() if x.name != "std"]

        # Iterate over the nodes available.
        # Doing in this way enable us to reuse the same logic, and therefore reduce the bug surface...

        for instance in root.topInstances:
            self.populate_component(comp, instance.body, False)
        for package in packages:
            self.populate_component(comp, package, True)

        # Extract the imports
        comp.imports = extract_imports(tree, self.sm)

        # Add some logs in the console :
        if self.ignored > 0:
            logger.debug(f"[INFO] Ignored {self.ignored} nodes from the source file.")

        # Finally, add the comments to the different elements.
        # As designed, this function is agnostic from the design type, and is already done within the IR reduction pass.
        comment_counts = len(comments.keys())
        count, miss, remaining, comp = self.linkComments(comp, comments)

        logger.info(
            f"[INFO] Attached {count} / {comment_counts} comment{"s" if count > 1 else ""} to the component."
        )
        if miss > 0:
            logger.warning(
                f"Found {miss} entit{"ies" if miss > 1 else "y"} that are not commented (Still {remaining} comment{"s" if remaining > 1 else ""} to be attached.). [file {file.name}]"
            )

        # Finally, call the IR to perform the matches
        comp = self.inferElements(comp)

        # Return the final component
        return comp
