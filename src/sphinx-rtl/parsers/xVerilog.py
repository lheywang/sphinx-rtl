# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Build the standard xVerilog (Verilog / SystemVerilog) parser.
# ----------------------------------------------------------------------------

# Imports
import pyslang
import pyslang.ast as ast
import pyslang.syntax as syntax
import logging
import re
import copy
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
)
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

        # No tools are needed, they're handled by the wheel !
        super().__init__()

        # Init the elements to induce the memory effect between the calls required by the Verilog specification.
        self.port = Port("unknown", "unknown", "unknown", ["none"])

        # Append the source manager :
        self.sm: SourceManager = SourceManager()

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
    # SYMBOLS BUILDERS
    # ----------------------------------------------------------------------------

    def build_port(self, node: ast.PortSymbol) -> Port:
        """
        Build a port object from the passed source !

        The code is crap, I know. But, due to the slight variations between each cases,
        it's hard to efficiently move to functions the redundant code. So, it work, I won't
        touch it...
        """

        # Get default values
        if node.name != "":
            self.port.name = node.name

        # Get the direction
        match node.direction:
            case ast.ArgumentDirection.In:
                self.port.direction = "input"
            case ast.ArgumentDirection.Out:
                self.port.direction = "output"
            case ast.ArgumentDirection.InOut:
                self.port.direction = "inout"

        # -------------------------------------------------------------------
        # PORT IS DECLARED AS ANSI
        # -------------------------------------------------------------------
        if node.isAnsiPort:

            # If Ansi port, the parameters are in the PortDeclarationSyntax:
            node_syntax: syntax.ImplicitAnsiPortSyntax = node.syntax.parent
            node_header: syntax.PortHeaderSyntax = node_syntax.header

            # We need to process the dimension of the "global" definition:
            raw_syntax = str(node_header.dataType).strip().split(" ", 1)

            # Update the type
            if raw_syntax[0] != "":
                self.port.hdl_type = raw_syntax[0].strip()

            # Extract the dimensions
            if len(raw_syntax) > 1:

                # Extract each pairs
                size_pairs = [
                    x.strip() for x in raw_syntax[1].replace("[", "").split("]")
                ]

                # Clear the list
                self.port.hdl_size = []

                # For each pairs, append one to the port
                for size_pair in size_pairs:
                    bounds = [x.strip() for x in size_pair.split(":")]

                    # If there's at least two bounds
                    if len(bounds) >= 2:
                        self.port.hdl_size.append(bounds[0])
                        self.port.hdl_size.append(bounds[1])

            else:
                self.port.hdl_size = ["0", "0"]

            # Finally, processing the last elements (a size that may be specific to the declaration)
            node_declarator: syntax.DeclaratorSyntax = node_syntax.declarator
            for dimension in node_declarator.dimensions:

                raw_dimension = str(dimension)
                size_pairs = [
                    x.strip()
                    for x in raw_dimension.replace("[", "").split("]")
                    if len(x) > 1
                ]

                # Attempt to split the pairs, if fail that's a Scalar
                for size_pair in size_pairs:
                    temp = size_pair.replace("::", ";;")
                    bounds = [x.strip() for x in temp.split(":")]

                    # scalar
                    if len(bounds) == 1:
                        if bounds[0].isdecimal():
                            self.port.hdl_size.append(
                                f"{int(bounds[0].replace(";;", "::")) - 1}"
                            )
                        else:
                            self.port.hdl_size.append(bounds[0].replace(";;", "::"))
                        self.port.hdl_size.append("0")

                    elif len(bounds) == 2:
                        self.port.hdl_size.append(bounds[0].replace(";;", "::"))
                        self.port.hdl_size.append(bounds[1].replace(";;", "::"))

            # Add the line
            source = self.sm.getLineNumber(node_declarator.sourceRange.start)
            if source > 0:
                self.port.line = source
            else:
                self.port.line = -1

        # -------------------------------------------------------------------
        # PORT IS DECLARED AS NON-ANSI
        # -------------------------------------------------------------------
        else:

            internal: ast.Symbol = node.internalSymbol

            decl_syntax: syntax.DeclaratorSyntax = internal.syntax
            parent: syntax.SyntaxNode = decl_syntax.parent

            # Fetch the parent node (sometimes not on the same place ...)
            data_type = None
            if hasattr(parent, "header") and hasattr(parent.header, "dataType"):
                data_type = parent.header.dataType
            elif hasattr(parent, "dataType"):
                data_type = parent.dataType

            # Extract the dimensions
            raw_syntax = str(data_type).strip().split(" ", 1)

            # Update the type
            if raw_syntax[0].strip():
                self.port.hdl_type = raw_syntax[0].strip()
            else:
                self.port.hdl_type = "logic"

            # Extract the dimensions
            if len(raw_syntax) > 1:

                # Extract each pairs
                size_pairs = [
                    x.strip() for x in raw_syntax[1].replace("[", "").split("]")
                ]

                # Clear the list
                self.port.hdl_size = []

                # For each pairs, append one to the port
                for size_pair in size_pairs:
                    temp = size_pair.replace("::", ";;")
                    bounds = [x.strip() for x in temp.split(":")]

                    # If there's at least two bounds
                    if len(bounds) >= 2:
                        self.port.hdl_size.append(bounds[0].replace(";;", "::"))
                        self.port.hdl_size.append(bounds[1].replace(";;", "::"))

            else:
                self.port.hdl_size = ["0", "0"]

            # Add the declarator part size
            for dimension in decl_syntax.dimensions:

                raw_dimension = str(dimension)
                size_pairs = [
                    x.strip()
                    for x in raw_dimension.replace("[", "").split("]")
                    if len(x) > 0
                ]

                # Attempt to split the pairs, if fail that's a Scalar
                for size_pair in size_pairs:
                    temp = size_pair.replace("::", ";;")
                    bounds = [x.strip() for x in temp.split(":")]

                    # scalar
                    if len(bounds) == 1:
                        if bounds[0].isdecimal():
                            self.port.hdl_size.append(
                                f"{int(bounds[0].replace(";;", "::")) - 1}"
                            )
                        else:
                            self.port.hdl_size.append(bounds[0].replace(";;", "::"))
                        self.port.hdl_size.append("0")

                    elif len(bounds) == 2:
                        self.port.hdl_size.append(bounds[0].replace(";;", "::"))
                        self.port.hdl_size.append(bounds[1].replace(";;", "::"))

            # Add the line
            source = self.sm.getLineNumber(node.location)
            if source > 0:
                self.port.line = source
            else:
                self.port.line = -1

        # Build the port
        return copy.deepcopy(self.port)

    def build_process(self, node: ast.ProceduralBlockSymbol) -> Process:
        """
        Build a process object from the passed source.
        """

        # hdl_type: str
        # signals_read: list[str]
        # signals_write: list[str]
        # hdl_clock: str = ""
        # hdl_reset: str = ""

        # Fetch the line of the process :
        line = self.sm.getLineNumber(node.location)

        # Get the name (generally empty)
        name = node.name

        # Init variables
        clocks: list[str] = []
        resets: list[str] = []
        targets: list[str] = []

        # Fetch the syntax
        node_syntax: syntax.ProceduralBlockSyntax = node.syntax
        statements: syntax.TimingControlStatementSyntax = node_syntax.statement

        # Fetch the type. We let it to None for cases
        hdl_type = None
        if (
            node.procedureKind == ast.ProceduralBlockKind.AlwaysFF
            or node.procedureKind == ast.ProceduralBlockKind.AlwaysLatch
        ):
            hdl_type = "flipflop"
        elif node.procedureKind == ast.ProceduralBlockKind.AlwaysComb:
            hdl_type = "comb"

        for statement in str(statements).split("\n"):
            assignements = statement.split("=")

            if len(assignements) > 1:
                lhs = assignements[0].strip()

                # That's a non blocking assignment !
                if "<" in lhs and lhs.split(" ")[0] not in targets:
                    targets.append(lhs.split(" ")[0])

        # First, fetch the procedural type:
        if hdl_type is None:
            if "posedge" in statements or "negedge" in statements:
                hdl_type = "flipflop"

        # Now, look for the clocks and resets :
        if hdl_type == "flipflop":

            # Fetch any markers within the passed tokens :
            markers = re.findall(
                r"(?:posedge|negedge)\s+([a-zA-Z_0-9]+)", str(statements)
            )

            # Identify clock and resets :
            for marker in markers:
                if any(kw in marker.lower() for kw in ("rst", "reset")):
                    resets.append(marker)
                else:
                    clocks.append(marker)

        # Fetch all the signals names
        signals = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_$]*\b", str(statements)))
        exclude = set(clocks) | set(resets)
        signals = signals - exclude

        # Add the line
        source = self.sm.getLineNumber(node.location)
        line = -1
        if source > 0:
            line = source
        else:
            line = -1

        # Build the output port
        return Process(
            name=name,
            hdl_type=str(hdl_type),
            hdl_clock=clocks,
            hdl_reset=resets,
            signals_write=targets,
            signals=list(signals),
            line=line,
        )

    def build_parameter(self, node: ast.ParameterSymbol) -> Parameter:
        """
        Build the parameter object from a passed parameter node.

        This one is really easy to do !
        """

        line = self.sm.getLineNumber(node.location)
        if not line > 0:
            line = -1

        return Parameter(
            name=str(node.name),
            hdl_type=str(node.type),
            hdl_value=str(node.value),
            line=line,
        )

    def build_signal(self, node: ast.VariableSymbol | ast.NetSymbol) -> Signal:
        """
        Build the signal object from a passed signal node.

        Another slightly different usage of the standard procedure matching,
        """

        line = self.sm.getLineNumber(node.location)
        if not line > 0:
            line = -1

        # Extract the name
        name = node.name.strip()

        parent: syntax.DataDeclarationSyntax = node.syntax.parent
        unpacked_dims = (
            [str(d).strip() for d in node.syntax.dimensions]
            if hasattr(node.syntax, "dimensions")
            else []
        )

        # Make the thing cleaner
        clean_type = re.sub(
            r"/\*.*?\*/|//.*", "", str(parent.type), flags=re.DOTALL
        ).strip()

        # Extract the dimensions
        raw_syntax = clean_type.strip().split(" ", 1)

        # Update the type
        hdl_type = "none"
        if raw_syntax[0].strip():
            hdl_type = raw_syntax[0].strip()
        else:
            hdl_type = "logic"

        # Clear the list
        hdl_size = []

        # Extract the dimensions
        if len(raw_syntax) > 1:

            # Extract each pairs
            size_pairs = [x.strip() for x in raw_syntax[1].replace("[", "").split("]")]

            # For each pairs, append one to the port
            for size_pair in size_pairs:
                temp = size_pair.replace("::", ";;")
                bounds = [x.strip() for x in temp.split(":")]

                # If there's at least two bounds
                if len(bounds) >= 2:
                    hdl_size.append(bounds[0].replace(";;", "::"))
                    hdl_size.append(bounds[1].replace(";;", "::"))

        else:
            hdl_size = ["0", "0"]

        # Add the declarator part size
        for raw_dimension in unpacked_dims:

            size_pairs = [
                x.strip()
                for x in raw_dimension.replace("[", "").split("]")
                if len(x) > 0
            ]

            # Attempt to split the pairs, if fail that's a Scalar
            for size_pair in size_pairs:
                temp = size_pair.replace("::", ";;")
                bounds = [x.strip() for x in temp.split(":")]

                # scalar
                if len(bounds) == 1:
                    if bounds[0].isdecimal():
                        hdl_size.append(f"{int(bounds[0].replace(";;", "::")) - 1}")
                    else:
                        hdl_size.append(bounds[0].replace(";;", "::"))
                    hdl_size.append("0")

                elif len(bounds) == 2:
                    hdl_size.append(bounds[0].replace(";;", "::"))
                    hdl_size.append(bounds[1].replace(";;", "::"))

        # Build the output node
        return Signal(
            name=name,
            hdl_type=hdl_type,
            hdl_size=hdl_size,
            hdl_value="unknown",
            line=line,
        )

    def build_assignment(self, node: ast.ContinuousAssignSymbol) -> Assignment:
        """
        Build the assignement object from a passed assign node.
        """

        # Extract the LHS and RHS
        syntax = str(node.syntax)
        assigns = syntax.split("=", 1)

        # Alloc output
        rhs = ""
        lhs = []

        if len(assigns) > 1:
            rhs = assigns[0].strip()
            lhs = list(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_$]*\b", assigns[1]))

        line = self.sm.getLineNumber(node.location)
        if not line > 0:
            line = -1

        # Build the output object
        return Assignment(
            target=rhs, source=lhs, isComb=False if len(lhs) == 1 else True, line=line
        )

    def build_enum(self, node: ast.TypeAliasType) -> Enum:
        """
        Build the enum definition from a TypeAlias node.
        """
        # Fetch the resolved type
        node_type: str = str(node.targetType.type)
        width = node.bitstreamWidth

        # Extract the elements
        enum, name = node_type.split("}", 1) if "}" in node_type else ("", "")

        # Allocate variables
        values: list[int] = []
        ids: list[str] = []

        # Extract the elements :
        if enum.startswith("enum{"):
            members = enum.split("enum{", 1)[1].split(",")

            # Extract the values
            for member in members:
                temp = member.split("=")

                if len(temp) > 1:
                    ids.append(temp[0])
                    values.append(int(temp[1].replace(f"{width}'d", "")))

        # Get the line
        line = self.sm.getLineNumber(node.location)
        if not line > 0:
            line = -1

        # Build the output
        return Enum(name=name.split(".")[-1], values=values, members=ids, line=line)

    def build_interfacePort(self, node: ast.InterfacePortSymbol) -> Port:
        """
        Extract the data from an Interface used as Port.
        """

        # Get the line
        line = self.sm.getLineNumber(node.location)
        if not line > 0:
            line = -1

        # Extract name
        name = node.name

        # Extract some infos
        raw_syntax = [
            x.strip() for x in str(node.syntax.parent).strip().split(" ") if len(x) > 0
        ]

        interface = "unknown"
        modport = "unknown"
        if len(raw_syntax) > 1 and raw_syntax[1] == name.strip():
            interface, modport = raw_syntax[0].split(".", 1)

        # Build the port we'll return :
        return Port(
            name=name,
            direction=modport,
            hdl_type=interface,
            hdl_size=["0", "0"],
            line=line,
        )

    def build_interface(self, node: ast.InstanceSymbol) -> Interface:
        """
        Build an interface from the passed node.
        """
        body: ast.InstanceBodySymbol = node.body
        print(body.definition)
        print(body.portList)
        print(body.parameters)

    # ----------------------------------------------------------------------------
    # COMMENT LINKER
    # ----------------------------------------------------------------------------
    def link_comments(
        self,
        elements: list[
            Port
            | Signal
            | Interface
            | Enum
            | Import
            | Signal
            | Process
            | Assignment
            | Parameter
        ],
        comments: tuple[int, str],
    ) -> list[
        Port
        | Signal
        | Interface
        | Enum
        | Import
        | Signal
        | Process
        | Assignment
        | Parameter
    ]:
        """
        Insert the comments that match the declaration line or the previous one into the element structure.
        Return the modified list.
        """
        pass

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
        assigns: list[Assignment] = []
        interfaces: list[Interface] = []

        # Run the tool to parse the file
        tree = syntax.SyntaxTree.fromFile(str(file))
        compilation = ast.Compilation()
        compilation.addSyntaxTree(tree)

        interfaces = []
        modules = []
        for member in tree.root.members:
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
            stub_tree = syntax.SyntaxTree.fromText(stub)
            compilation.addSyntaxTree(stub_tree)

        # Iterate over the different nodes :
        root = compilation.getRoot()
        self.sm = compilation.sourceManager
        for instance in root.topInstances:

            # List to track if the port name is already known, or not ?!?
            ports_names = []
            if isinstance(instance, ast.InstanceSymbol):
                for m in instance.body:

                    match m.kind:
                        case ast.SymbolKind.Parameter:
                            parameters.append(self.build_parameter(m))

                        case ast.SymbolKind.TypeAlias:
                            enums.append(self.build_enum(m))

                        case (
                            ast.SymbolKind.WildcardImport
                            | ast.SymbolKind.ExplicitImport
                        ):
                            print(f"Import : {type(m)}")

                        case ast.SymbolKind.Port:
                            # Add the port here
                            ports_names.append(m.name)
                            ports.append(self.build_port(m))

                        case ast.SymbolKind.InterfacePort:
                            ports_names.append(m.name)
                            ports.append(self.build_interfacePort(m))

                        case ast.SymbolKind.Net | ast.SymbolKind.Variable:
                            if m.name not in ports_names:
                                signals.append(self.build_signal(m))

                        case ast.SymbolKind.ProceduralBlock:
                            processes.append(self.build_process(m))

                        case ast.SymbolKind.ContinuousAssign:
                            assigns.append(self.build_assignment(m))

                        case ast.SymbolKind.Instance:
                            interfaces.append(self.build_interface(m))

                        # We don't care about these, they're proxies to enums and other stuff like that
                        case ast.SymbolKind.TransparentMember:
                            pass

                        case _:
                            print(m.kind)

        # Finally, add the comments to the different elements

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
