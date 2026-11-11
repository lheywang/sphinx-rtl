# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    30/09/2026
#
# Brief :   A CLI entry to use the tool as a standalone executable,
#           for example to dump the structure as a JSON format ...
# ----------------------------------------------------------------------------

# Imports
import argparse
import runpy
import sys
import time

import importlib.metadata as meta

from pathlib import Path

from sphinx_rtl.models import (
    RTLConfig,
    ComponentConfig,
    Component,
    serialize_components,
    standard_cleanup,
)
from sphinx_rtl.RTLParser2 import RTLParser2
from sphinx_rtl.RTLAnalyse import RTLAnalyse

import logging

logger = logging.getLogger(__name__)


# Utility functions
def setup():
    """
    Configure the environment to run nicely, even in CLI mode.
    """
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)


# Entry point
def cli():
    # Setup the environment
    setup()

    # Configure the parser
    parser = argparse.ArgumentParser()
    parser.description = "A sphinx extension to build documentation for Hardware RTL, by an RTL engineer !"
    parser.epilog = f"Built by l.heywang."
    parser.add_argument("-v", "--version", action="store_true", default=False)
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Provide a Python script to configure the system.",
    )
    parser.add_argument(
        "-f",
        "--files",
        nargs="+",
        help="RTL files to analyse (could be direct file, glob or large globs)",
    )
    parser.add_argument(
        "--cleanup",
        type=str,
        help="Define the cleanup function to be used within the configuration file.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Is there the version string ?
    if args.version:
        print("---")
        print(" sphinx-rtl")
        print("   A Python extension to generate documentation for your RTL projects.")
        print(f"   Version : {meta.version("sphinx-rtl")}")
        print()
        print("   Built by l.heywang on November 2026.")
        print("---")

    # Is there a configuration file ?
    config, comps = RTLConfig(), ComponentConfig()
    namespace = None
    if args.config:
        conf = Path(args.config)
        if not conf.is_file():
            raise FileNotFoundError(f"Could not find configuration file ({conf})")

        namespace = runpy.run_path(str(conf))

        # Is there our configurations ?
        if "rtl_config" not in namespace:
            raise AttributeError(
                f"The configuration file ({conf}) must define a variable 'rtl_config' of type RTLConfig in it."
            )
        config = namespace["rtl_config"]

        if "comp_config" not in namespace:
            raise AttributeError(
                f"The configuration file ({conf}) must define a variable 'comp_config' of type ComponentConfig in it."
            )
        comps = namespace["components"]

        if not isinstance(config, RTLConfig):
            raise TypeError(
                "The provided config variable is not an instance of 'RTLConfig'."
            )
        if not isinstance(comps, ComponentConfig):
            raise TypeError(
                "The provided comp_config variable is not an instance of 'ComponentConfig'."
            )

    # Now, we we can parse all files
    database: dict[str, Component] = {}

    for file in args.files:

        ts = time.time()

        parser = RTLParser2()
        components = parser.parse(Path(file))

        for component in components.values():

            # Update the component config
            component.render = config.merge(component.render)
            component.config = comps.merge(component.config)

            # Insert into the dict
            database[component.name] = component

        tt = time.time()
        logger.info(f"[INFO] Processed {file} in {(tt - ts) * 1000:.3f} ms.")

    # Now, run the analysis on it
    ts = time.time()
    logger.info(f"[INFO] Analyzing components ...")
    analyzer = RTLAnalyse(None, None)
    analyzer.analyse(database)
    tt = time.time()
    logger.info(f"[INFO] Done in {(tt - ts) * 1000:.3f} ms.")

    logger.info(f"[INFO] Exporting components ...")
    ts = time.time()

    # First, export the fully qualified elements
    for output in config.public_output:

        # Resolve the target path
        target = Path(output)
        target.parent.mkdir(exist_ok=True, parents=True)

        # Serialize the output
        logger.info(f"[INFO] Writing full database : {target}")
        serialize_components(list(database.values()), target)

    # Then, export the private elements
    for output in config.private_output:

        # Resolve the target path
        target = Path(output)
        target.parent.mkdir(exist_ok=True, parents=True)

        # Request for the callback
        if args.cleanup:
            logger.info(f"[INFO] Executing custom cleanup snippet...")
            local_scope = {"db": database, "database": database}
            global_scope = namespace if "namespace" in locals() else globals()
            exec(args.cleanup, global_scope, local_scope)

            database = local_scope.get("database", local_scope.get("db", database))
            cleaned = list(database.values())
        else:
            cleaned = standard_cleanup(list(database.values()))

        # Now, we can export them
        logger.info(f"[INFO] Writing stripped database : {target}")
        serialize_components(cleaned, target)

    tt = time.time()
    logger.info(f"[INFO] Done in {(tt - ts) * 1000:.3f} ms.")


if __name__ == "__main__":
    cli()
