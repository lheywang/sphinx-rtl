# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Define the render module, to transform Components into
#           Sphinx docutils node syntax.
# ----------------------------------------------------------------------------

# Imports
from docutils import nodes
from sphinx.util import logging
from sphinx._cli.util.colour import bold
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from pathlib import Path
from docutils.nodes import make_id

from sphinx_rtl.RTLRender.helpers import (
    BadgeColor,
    render_ref,
)
from .renderer import (
    AssignRTLRender,
    EnumRTLRender,
    FileInfoRTLRender,
    FunctionRTLRender,
    ImportRTLRender,
    ModportRTLRender,
    ModuleRTLRender,
    ParameterRTLRender,
    PortRTLRender,
    ProcessRTLRender,
    RegisterRTLRender,
    SignalRTLRender,
    SourceRTLRender,
    StructureRTLRender,
    TemplateRTLRender,
    RTLRenderUtils,
)
from sphinx_rtl.models import Component, Signal, Port

# Configure the logger
logger = logging.getLogger(__name__)


class RTLRender:
    """
    Render a passed component into docutils nodes.
    """

    # Colors for the different variants elements (clocks and resets ...)
    DOMAIN_COLORS = [
        BadgeColor.RED,
        BadgeColor.CYAN,
        BadgeColor.GREEN,
        BadgeColor.BLUE,
        BadgeColor.GRAY,
        BadgeColor.ORANGE,
    ]

    # --------------------------------------------------------------------------------
    # BUILTINS
    # --------------------------------------------------------------------------------

    def __init__(self, app: Sphinx, env: BuildEnvironment):
        """
        Init the render class
        """

        # Set the base doc to use in any cases. Will be replaced later anyway ...
        self.base_doc = Path(__file__)

        # Fetch the application
        self.app = app
        self.env = env

        # Build the reference base list
        self.refs: list[dict] = []

        # Compose the class
        self.assign = AssignRTLRender(self)
        self.enum = EnumRTLRender(self)
        self.file_info = FileInfoRTLRender(self)
        self.function = FunctionRTLRender(self)
        self.imports = ImportRTLRender(self)
        self.modport = ModportRTLRender(self)
        self.module = ModuleRTLRender(self)
        self.parameter = ParameterRTLRender(self)
        self.port = PortRTLRender(self)
        self.process = ProcessRTLRender(self)
        self.register = RegisterRTLRender(self)
        self.signal = SignalRTLRender(self)
        self.source = SourceRTLRender(self)
        self.structure = StructureRTLRender(self)
        self.template = TemplateRTLRender(self)

        # Internal utils
        self.utils = RTLRenderUtils(self)

        return

    # --------------------------------------------------------------------------------
    # PUBLIC FUNCTIONS
    # --------------------------------------------------------------------------------

    def render(
        self, component: Component | None, base_doc: Path
    ) -> tuple[nodes.container, list[dict]]:
        """
        Render a component into an AST of nodes.

        This function is the generic entry, and will call the correct function as well as creating the root component.
        For a more specific render, you can call :
            - render_as_package
            - render_as_module
            - render_as_testbench
            - render_as_module.

        This is, however not really recommended as this could lead with missing elements for a module.
        """

        # First, fetch our root node :
        root = nodes.container(is_div=True, classes=["rtl-component-view"])

        if component is None:
            logger.error("Provided component is None. Could not render anything.")
            return (root, self.refs)

        # Update the base doc
        self.base_doc = base_doc

        # Now, we can safely render the component.
        # Any option will be valid, regardless of it's composition.
        match component.comp_type:
            case "testbench":
                logger.info(
                    bold(
                        f"[INFO] --- Rendering {f'{component.name} ' if component.name != "" else ""}as a testbench."
                    )
                )
                return self.render_as_testbench(component=component, root=root)

            case "package":
                logger.info(
                    bold(
                        f"[INFO] --- Rendering {f'{component.name} ' if component.name != "" else ""}as a package."
                    )
                )
                return self.render_as_package(component=component, root=root)

            case "interface":
                logger.info(
                    bold(
                        f"[INFO] --- Rendering {f'{component.name} ' if component.name != "" else ""}as an interface."
                    )
                )
                return self.render_as_interface(component=component, root=root)

            # If nothing was found, try as a module.
            # This is the most complete, exception shall not be fully wrong if nothing is present.
            case _:
                logger.info(
                    bold(
                        f"[INFO] --- Rendering {f'{component.name} ' if component.name != "" else ""}as a module."
                    )
                )
                return self.render_as_module(component=component, root=root)

        # Return the default value is nothing was found.
        return (root, self.refs)

    def render_as_package(
        self, root: nodes.container, component: Component
    ) -> tuple[nodes.container, list[dict]]:
        """
        Render the provided component as a package.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name
        context = self.create_section(root, component.name, sec_name=context_name)

        # Common module header
        self.file_info.render(context, component)

        # Emit an event before the elements rendering
        self.app.emit("rtl-post-card-rendering", self.app, self.env, context, component)

        # Add the elements we need here.
        self.imports.render(context, component)
        self.parameter.render(context, component)
        self.enum.render(context, component)
        self.function.render(context, component)
        self.structure.render(context, component)
        self.source.render(context, component)

        # Add a separator last
        self.add_separator(context)

        # Emit an event after the elements rendering
        self.app.emit(
            "rtl-post-elements-rendering", self.app, self.env, context, component
        )

        # Return the global node
        return (root, self.refs)

    def render_as_module(
        self, root: nodes.container, component: Component
    ) -> tuple[nodes.container, list[dict]]:
        """
        Render the provided component as a module.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name
        context = self.create_section(root, component.name, sec_name=context_name)

        # Common module header
        self.file_info.render(context, component)

        # Emit an event before the elements rendering
        self.app.emit("rtl-post-card-rendering", self.app, self.env, context, component)

        # Add the elements we need here.
        self.register.render(context, component)
        self.imports.render(context, component)
        self.parameter.render(context, component)
        self.port.render(context, component)
        self.enum.render(context, component)
        self.module.render(context, component)
        self.process.render(context, component)
        self.signal.render(context, component)
        self.assign.render(context, component)
        self.template.render(context, component)
        self.source.render(context, component)

        # Add a separator last
        self.add_separator(context)

        # Emit an event after the elements rendering
        self.app.emit(
            "rtl-post-elements-rendering", self.app, self.env, context, component
        )

        # Return the global node
        return (root, self.refs)

    def render_as_testbench(
        self, root: nodes.container, component: Component
    ) -> tuple[nodes.container, list[dict]]:
        """
        Render the provided component as a testbench.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name
        context = self.create_section(root, component.name, sec_name=context_name)

        # Common module header
        self.file_info.render(context, component)

        # Emit an event before the elements rendering
        self.app.emit("rtl-post-card-rendering", self.app, self.env, context, component)

        # Add a separator last
        self.add_separator(context)

        # Add the elements we need here.
        self.imports.render(context, component)
        self.parameter.render(context, component)
        self.signal.render(context, component)
        self.module.render(context, component)
        self.process.render(context, component)
        self.source.render(context, component)

        # Emit an event after the elements rendering
        self.app.emit(
            "rtl-post-elements-rendering", self.app, self.env, context, component
        )

        # Return the global node
        return (root, self.refs)

    def render_as_interface(
        self, root: nodes.container, component: Component
    ) -> tuple[nodes.container, list[dict]]:
        """
        Render the provided component as an interface.
        """
        # We may be called within the same file for different modules, so first, create our section
        try:
            context_name = str(
                Path(component.file.path).relative_to(Path(component.file.repo_path))
            )
        except ValueError:
            context_name = component.file.name

        context = self.create_section(root, component.name, sec_name=context_name)

        # Common module header
        self.file_info.render(context, component)

        # Emit an event before the elements rendering
        self.app.emit(
            "rtl-pre-elements-rendering", self.app, self.env, context, component
        )

        # Add the elements we need here.
        self.imports.render(context, component)
        self.parameter.render(context, component)
        self.port.render(context, component)
        self.modport.render(context, component)
        self.source.render(context, component)

        # Add a separator last
        self.add_separator(context)

        # Emit an event after the elements rendering
        self.app.emit(
            "rtl-post-elements-rendering", self.app, self.env, context, component
        )

        # Return the global node
        return (root, self.refs)

    def add_separator(self, root: nodes.section) -> None:
        """
        Add the final separator to the component.
        """

        divider = nodes.transition()
        root += divider

    def create_section(
        self,
        root: nodes.container | nodes.section,
        name: str,
        id: str = "",
        sec_name: str = "",
    ) -> nodes.section:
        """
        Create a section within the current context, and return it.
        """
        norm_name = name.removesuffix("s")

        if id:
            section = nodes.section(ids=[make_id(f"{id}-{norm_name}")])
        else:
            section = nodes.section(ids=[make_id(norm_name)])
        section += nodes.title(text=name)
        section += render_ref(name, id, "", self.refs)

        if sec_name != "":
            p = nodes.paragraph()
            p += nodes.Text(sec_name)
            section += p
        root += section

        return section
