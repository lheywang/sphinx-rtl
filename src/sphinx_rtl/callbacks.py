# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    09/10/2026
#
# Brief :   All of the different callbacks to be used within the project
# ----------------------------------------------------------------------------

# Imports
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging
from sphinx._cli.util.colour import bold, blue, darkgray
from sphinx_rtl.RTLConfig import RTLConfig
from sphinx_rtl.RTLAnalyse import RTLAnalyse
from sphinx_rtl.RTLDomain import RTLDomain
from sphinx_rtl.models import (
    Component,
    serialize_components,
    load_components,
    standard_cleanup,
)

# Configure the logger
logger = logging.getLogger(__name__)


# Callbacks
def on_builder_inited(app: Sphinx) -> None:
    """
    Initialize the different classes and engines.
    """
    root_dir = Path(app.confdir)
    # config = RTLConfig.discover(root_dir)
    domain: RTLDomain = app.env.get_domain("rtl")  # type: ignore
    # domain.data["base_config"] = config


def on_env_get_outdated(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """
    Fetch all the dependencies of the changed names to be rebuilt.
    """
    domain: RTLDomain = env.get_domain("rtl")  # type: ignore
    extra = domain.get_outdated(env)

    logger.info(bold(f"[INFO] Found {len(extra)} files that need to be re-read."))
    return extra


def on_env_updated(app: Sphinx, env: BuildEnvironment) -> list[str]:

    # Fetch the different elements
    domain: RTLDomain = env.get_domain("rtl")  # type: ignore
    components = domain.data.get("components", {})

    # Before running the analysis, import the external components
    cfg: RTLConfig = getattr(app.config, "rtl_config", RTLConfig())
    logger.info(bold("[INFO] Importing components ..."))

    for source in cfg.external_stubs:

        # Resolve the target path
        target = (Path(app.confdir) / Path(source)).resolve()

        # Load the components
        loaded = load_components(target)

        # Build the components dict
        loaded_dict = dict((x.name, x) for x in loaded)

        # Inserting the dict into the components
        components = loaded_dict | components

        # Logs
        logger.info(
            blue(
                f"[INFO] Loaded {len(loaded_dict.keys())} component{"s" if len(loaded_dict.keys()) > 1 else ""} from {target}"
            )
        )

    # Perform the analysis
    engine = RTLAnalyse(app, env)
    engine.analyse(components)

    # Update the components
    domain.data["components"] = components

    # Exit
    return []


def on_build_finished(app: Sphinx, exception: Exception | None) -> None:
    """
    Build the output files as the serialized JSON output.
    """

    # Exit on any exception
    if exception is not None:
        return

    # Fetch the domain
    domain: RTLDomain = app.env.get_domain("rtl")  # type: ignore
    components: dict[str, Component] = domain.data.get("components", {})
    if not components:
        return

    # Fetch the config
    cfg: RTLConfig = getattr(app.config, "rtl_config", RTLConfig())
    logger.info(bold("[INFO] Performing exports ..."))

    # First, export the fully qualified elements
    for output in cfg.public_output:

        # Resolve the target path
        target = Path(app.outdir) / Path(output)
        target.parent.mkdir(exist_ok=True, parents=True)

        # Serialize the output
        logger.info(blue(f"[INFO] Writing full database : {target}"))
        serialize_components(list(components.values()), target)

    # Then, export the private elements
    for output in cfg.private_output:

        # Resolve the target path
        target = Path(app.outdir) / Path(output)
        target.parent.mkdir(exist_ok=True, parents=True)

        # Request for the callback
        cleaned: list[Component] = app.emit(
            "rtl-pre-private-export", app, app.env, list(components.values())
        )

        # Did someone cleaned us the components ?
        if len(cleaned) == 0:
            logger.info(
                darkgray(
                    "[INFO] No callbacks were called for the cleanup. Using the default cleaning method."
                )
            )
            cleaned = standard_cleanup(list(components.values()))

        # Now, we can export them
        logger.info(blue(f"[INFO] Writing stripped database : {target}"))
        serialize_components(cleaned, target)


def on_missing_reference(app: Sphinx, env: BuildEnvironment, node, contnode):
    """
    Try to resolve a missing reference somewhere.
    This act as a second layer, therefore we try to limit the damages rather than operating ideally.
    This essentially goes by referencing to the nearest node available.
    """
    refdomain = node.get("refdomain")
    if refdomain == "rtl" or refdomain is None:
        domain: RTLDomain = env.get_domain("rtl")  # type: ignore
        target = node.get("reftarget")
        typ = node.get("reftype", "any")
        fromdoc = env.docname

        return domain.resolve_missing_xref(
            env, fromdoc, app.builder, typ, target, node, contnode
        )
    return None
