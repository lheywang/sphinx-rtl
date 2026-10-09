# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Import the RTL Domain to be used for all the RTL components.
# ----------------------------------------------------------------------------

# Imports
from collections.abc import Iterable

from docutils import nodes
from typing import AbstractSet, Any
from sphinx.addnodes import pending_xref
from sphinx.builders import Builder
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.nodes import make_refnode
from sphinx_rtl.models import Component

# Configure the logger
logger = logging.getLogger(__name__)


# Class
class RTLDomain(Domain):
    """
    Handle the reference linking on the global project.
    """

    # Basic config
    name = "rtl"
    label = "RTL Domain"
    data_version = 1

    # Data storage
    initial_data = {
        "symbols": {},  # -> dict[target_id, tuple[str, str, str, str]]
        "components": {},  # -> dict[str, Component]
        "file_doc": {},  # -> dict[filepath, docname]. Act a lock for unique docnames.
        "doc_files": {},  # -> dict[docname, list[str]]
        "doc_globs": {},  # -> dict[docname, set[str]]
    }

    # Object config
    object_types = {
        "module": ObjType("module", "module"),
        "port": ObjType("port", "port"),
        "parameter": ObjType("parameter", "parameter"),
        "enum": ObjType("enum", "enum"),
        "signal": ObjType("signal", "signal"),
        "process": ObjType("process", "process"),
        "structure": ObjType("structure", "structure"),
        "function": ObjType("function", "function"),
    }

    # Roles
    roles = {
        "module": XRefRole(),
        "port": XRefRole(),
        "parameter": XRefRole(),
        "enum": XRefRole(),
        "signal": XRefRole(),
        "process": XRefRole(),
        "structure": XRefRole(),
        "function": XRefRole(),
    }

    # --------------------------------------------------------------------
    # CACHE MANAGEMENT
    # --------------------------------------------------------------------

    def clear_doc(self, docname: str) -> None:
        """
        Clear the cache for a target source file.
        """

        # Clear symbols
        self.data[docname] = {
            target_id: sym
            for target_id, sym in self.data["symbols"].items()
            if sym["docname"] != docname
        }

        # Clear the associated file names.
        files = self.data["doc_files"].pop(docname, set())
        for f in files:
            self.data["file_doc"].pop(f, None)
        self.data["doc_globs"].pop(docname, None)

        logger.info("[INFO] Cleaned up the RTLDomain cache")

    def merge_domaindata(
        self, docnames: AbstractSet[str], otherdata: dict[str, Any]
    ) -> None:
        """
        Merge two domains to ensure an operation even on parallel builds.
        """
        count = 0

        # Merge symbols
        for target_id, sym in otherdata.get("symbols", {}).items():
            if sym["docname"] in docnames:
                self.data["symbols"][target_id] = sym
                count += 1

        # Merge components
        for comp in otherdata.get("component", {}).values():
            self.add_component(comp)
            count += 1

        # Merge files
        for doc in docnames:
            if doc in otherdata.get("doc_files", {}):
                self.data["doc_files"][doc] = otherdata["doc_files"][doc]
            if doc in otherdata.get("doc_globs", {}):
                self.data["doc_globs"][doc] = otherdata["doc_globs"][doc]
        self.data["file_doc"].update(otherdata.get("file_doc", {}))
        self.data["components"].update(otherdata.get("components", {}))

        if count > 0:
            logger.info(
                f"[INFO] Merged {count} reference{"s" if count > 1 else ""} into the master domain."
            )

    # --------------------------------------------------------------------
    # REFERENCE ADD
    # --------------------------------------------------------------------
    def add_symbol(
        self, target_id: str, name: str, obj_type: str, docname: str, comp: str = ""
    ) -> None:
        """
        Register a new reference into the domain.
        """
        norm = nodes.make_id(target_id)
        self.data["symbols"][norm] = {
            "name": name,
            "comp": comp,
            "type": obj_type,
            "docname": docname,
        }

    def add_symbol_batch(self, refs: list[dict], docname: str) -> None:
        """
        Register a list of references, built by the render engine.
        """
        count = 0
        for ref in refs:
            target_id = nodes.make_id(ref["target_id"])

            self.data["symbols"][target_id] = {
                "name": ref["name"],
                "comp": ref.get("comp", ""),
                "type": ref.get("type", "port"),
                "docname": docname,
            }
            count += 1

        if count > 0:
            logger.info(
                f"[INFO] Imported {count} reference{"s" if count > 1 else ""} into the domain."
            )

    # --------------------------------------------------------------------
    # COMPONENT MANAGEMENT
    # --------------------------------------------------------------------
    def add_component(self, component: Component) -> None:
        """
        Add a component to the internal knowledge base.
        """
        if component is None:
            return

        if component.name not in self.data["components"].keys():
            self.data["components"][component.name] = component
            return

        logger.warning(
            f"Duplicate component (name={component.name}) insertion required. Action ignored."
        )
        return

    # --------------------------------------------------------------------
    # LINK RESOLUTION
    # --------------------------------------------------------------------
    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: pending_xref,
        contnode: nodes.Element,
    ) -> nodes.reference | None:
        """
        Resolve a pending xref from the internal list.
        """

        # Normalize and fetch the request
        norm = nodes.make_id(target)
        sym = self.data["symbols"].get(norm)

        # Did we fetched anything ?
        if not sym:
            return None

        # Build the reference
        title = f"{sym["comp"]}.{sym["name"]}" if sym["comp"] else sym["name"]
        refnode = make_refnode(
            builder,
            fromdocname=fromdocname,
            todocname=sym["docname"],
            targetid=norm,
            child=contnode,
            title=title,
        )
        return refnode

    def get_objects(self) -> Iterable[tuple[str, str, str, str, str, int]]:
        """
        Return the objects from the internal table for the internal links and tables.
        """
        for target_id, sym in self.data["symbols"].items():
            disp = f"{sym['comp']}.{sym['name']}" if sym["comp"] else sym["name"]
            yield (target_id, disp, sym["type"], sym["docname"], target_id, 1)
