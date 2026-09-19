# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Build the standard xVerilog (Verilog / SystemVerilog) parser.
# ----------------------------------------------------------------------------

# Imports
import json
import logging
from pathlib import Path

from ..models import Component, Parameter, Port, Enum, Import, Signal, Process
from .xParser import xParser

# Logger config
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

        # Look for the tool we need
        super().__init__("verible-verilog-syntax")

        # Initialize our state
        self.current_direction = "input"
        self.VALID_DIRECTIONS = ["input", "output", "inout", "ref"]

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
    # NODES PARSERS
    # ----------------------------------------------------------------------------

    def _parse_kModuleHeader(self, node):
        """
        Parse the module header and return the name of en entity.
        """
        return ""

    def _parse_kPortDeclaration(self, node) -> Port:
        """
        Parse the AST for a port declaration.
        """

        # Port name
        # The port name is under a SymbolIdentifier, on a root branch, therefore level MUST be low.
        name_nodes = list(
            self.find(
                node,
                "SymbolIdentifier",
                "children",
                exclude=["kDataType", "kInterfacePortHeader"],
            )
        )
        if name_nodes:
            _, id_node = min(name_nodes, key=lambda item: item[0])
            port_name = id_node.get("text", "unknown")

        # Port direction
        # We only look for the first ones, as they're on top.
        children = node.get("children", [])
        for child in children[:2]:
            if isinstance(child, dict):
                tag = self.get(child, "tag")
                if tag in self.VALID_DIRECTIONS:
                    self.current_direction = tag

        direction = self.current_direction

        # HDL Type
        # May be set in a different places. First, look on kDataPrimitiveType
        hdl_type = "unknown"
        data_type_nodes = list(self.find(node, "kDataType", "children"))
        _, type_node = data_type_nodes[0]

        if data_type_nodes:
            primary = list(self.find(type_node, "kDataTypePrimitive", "children"))

            # Check if we matched a primary type
            if primary:
                _, prim_node = primary[0]

                for child in prim_node.get("children", []):
                    if child and "tag" in child:
                        hdl_type = child["tag"]
                        break

            # Else, look for a more complex type
            # This also cover the interface types
            else:
                custom = list(
                    self.find(
                        type_node,
                        "SymbolIdentifier",
                        "children",
                        exclude=["kPackedDimensions", "kUnpackedDimensions"],
                    )
                )

                if custom:
                    tmp = []
                    for _, custom_node in custom:
                        tmp.append(self.get(custom_node, "text"))

                    # Build the type by joining them with a dot
                    hdl_type = ".".join(tmp)

        # Finally, extract the width
        hdl_size = []
        size_nodes = list(self.find(node, "kDimensionRange", "children"))

        # If kDimensionRange exist :
        if size_nodes:
            for _, range_node in size_nodes:
                direct_exprs = [
                    child
                    for child in range_node.get("children", [])
                    if child and child.get("tag") == "kExpression"
                ]

                hdl_size.append(
                    [
                        self.flatten(expr, ["text", "tag"], "children")
                        for expr in direct_exprs
                    ]
                )

        else:
            hdl_size = []

        # Build and return the port as we built
        return Port(
            name=port_name, direction=direction, hdl_type=hdl_type, hdl_size=hdl_size
        )

    def _parse_kAlwaysStatement(self, node) -> Process:
        pass

    # ----------------------------------------------------------------------------
    # AST PARSERS
    # ----------------------------------------------------------------------------

    def parse_ast(self, ast: dict) -> tuple[
        str,
        list[Parameter],
        list[Port],
        list[Enum],
        list[Import],
        list[Signal],
        list[Process],
    ]:
        """
        Walk on the AST tree and extract the different elements that we must know.
        """
        name = ""
        parameters: list[Parameter] = []
        ports: list[Port] = []
        enums: list[Enum] = []
        imports: list[Import] = []
        signals: list[Signal] = []
        processes: list[Process] = []

        for node in self.walk(ast):
            tag = node.get("tag")

            if tag == "kModuleHeader":
                name = self._parse_kModuleHeader(node)
            elif tag == "kPortDeclaration":
                port = self._parse_kPortDeclaration(node)
                if port:
                    ports.append(port)
            elif tag == "kAlwaysStatement":
                proc = self._parse_kAlwaysStatement(node)
                if proc:
                    processes.append(proc)
            else:
                # print(tag)
                pass

        print(ports)

        return name, parameters, ports, enums, imports, signals, processes

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

        # Run the tool to parse the file
        stdout = self.runTool(f"--printtree --export_json {str(file)}")
        ast = json.loads(stdout).get(str(file))

        # Parse the AST then
        name, parameters, ports, enums, imports, signals, processes = self.parse_ast(
            ast.get("tree", dict())
        )

        # Return the final component
        return Component(
            name=name,
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
