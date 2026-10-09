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
from sphinx_rtl.RTLConfig import RTLConfig

# Configure the logger
logger = logging.getLogger(__name__)


# Callbacks
def on_builder_inited(app: Sphinx) -> None:
    """
    Initialize the different classes and engines.
    """
    root_dir = Path(app.confdir)
    config = RTLConfig.discover(root_dir)
    domain = app.env.get_domain("rtl")
    domain.data["base_config"] = config


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
    logger.info(
        f">>> [EVENT: 2. env-get-outdated] Added: {len(added)}, Changed: {len(changed)}, Removed: {len(removed)}"
    )
    return []


def on_env_updated(app: Sphinx, env: BuildEnvironment) -> list[str]:

    logger.info(">>> [EVENT: 3. env-updated] Execution de l'analyse globale")
    domain = env.get_domain("rtl")
    components = domain.data.get("components", {})
    logger.info(f"[ANALYSE] {len(components)} composant(s) à ordonnancer dans le DAG.")

    return []
