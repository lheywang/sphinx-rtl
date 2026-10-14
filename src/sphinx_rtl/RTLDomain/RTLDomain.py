# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Import the RTL Domain to be used for all the RTL components.
# ----------------------------------------------------------------------------

# Imports
import glob
from collections.abc import Iterable
from docutils import nodes
from docutils.nodes import make_id
from typing import AbstractSet, Any
from sphinx.addnodes import pending_xref
from sphinx.builders import Builder
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx._cli.util.colour import blue, darkgray
from sphinx.util.nodes import make_refnode
from pathlib import Path
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
        "comp_to_doc": {},  # -> dict[comp_name, docname]
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

        logger.info(darkgray("[INFO] Cleaned up the RTLDomain cache"))

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

        # Merge files and files
        for doc in docnames:
            for comp in otherdata.get("component", {}).values():
                self.add_component(comp, doc)
                count += 1
            if doc in otherdata.get("doc_files", {}):
                self.data["doc_files"][doc] = otherdata["doc_files"][doc]
            if doc in otherdata.get("doc_globs", {}):
                self.data["doc_globs"][doc] = otherdata["doc_globs"][doc]
        self.data["file_doc"].update(otherdata.get("file_doc", {}))
        self.data["components"].update(otherdata.get("components", {}))

        if count > 0:
            logger.info(
                blue(
                    f"[INFO] Merged {count} reference{"s" if count > 1 else ""} into the master domain."
                )
            )

    def get_outdated(self, env: BuildEnvironment):
        """
        Examine all known globs and return the outdated components.
        """
        outdated: list[str] = []
        doc_files = self.data.get("doc_files", {})
        doc_globs = self.data.get("doc_globs", {})

        src_dir = Path(env.srcdir)

        for docname, patterns in doc_globs.items():
            current_match: set[str] = set()

            for pattern in patterns:
                resolved = (
                    pattern if Path(pattern).is_absolute() else str(src_dir / pattern)
                )
                for f in glob.glob(resolved, recursive=True):
                    current_match.add(str(Path(f).resolve()))

            known_files = doc_files.get(docname, set())

            if current_match != known_files:
                outdated.append(docname)

        return outdated

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
                blue(
                    f"[INFO] Imported {count} reference{"s" if count > 1 else ""} into the domain."
                )
            )

    # --------------------------------------------------------------------
    # COMPONENT MANAGEMENT
    # --------------------------------------------------------------------
    def add_component(self, component: Component | None, docname: str) -> None:
        """
        Add a component to the internal knowledge base.
        """
        if component is None:
            return

        if component.name not in self.data["components"].keys():
            self.data["components"][component.name] = component
            self.data["comp_to_doc"][component.name] = docname
            return

        logger.warning(
            f"Duplicate component (name={component.name}) insertion required. Action ignored."
        )
        return

    def register_file_to_doc(
        self, filepath: str | Path, docname: str, glob: str | None = None
    ) -> bool:
        """
        Link an RTL source to a sphinx document.

        Return false if the document is already associated with another file.
        """

        path_str = str(Path(filepath).resolve())

        # Is this file unique ?
        existing = self.data["file_doc"].get(path_str)
        if existing and existing != docname:
            logger.warning(
                f"Conflict : {path_str} is already claimed by {existing}. Ignored link.",
                location=docname,
            )
            return False

        # Locking the file
        self.data["file_doc"][path_str] = docname
        self.data["doc_files"].setdefault(docname, set()).add(path_str)

        if glob:
            self.data["doc_globs"].setdefault(docname, set()).add(glob)

        self.env.note_dependency(path_str)
        return True

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

    def resolve_missing_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Any,
        typ: str,
        target: str,
        node: nodes.Element,
        contnode: nodes.Element,
    ) -> nodes.Element | None:
        """
        Resolve missing xref by searching for the nearest element that could match.
        Not perfect, but better than anything.
        """

        components = self.data.get("components", {})
        comp_doc = self.data.get("comp_to_doc", {})

        # Fetch the known slugs
        slug_map = {name.lower().replace("_", "-"): name for name in components}

        # Sort by length to ensure we always find the most precise slug first
        sorted_slugs = sorted(slug_map.keys(), key=len, reverse=True)

        # Normalize slug
        target_slug = target.lower()
        parent_slug = None
        real_parent_name = None

        # Search for a known parent.
        for slug in sorted_slugs:
            if target_slug.startswith(slug):
                parent_slug = slug
                real_parent_name = slug_map[slug]
                break

        # Did we find any valid parents ?
        if not real_parent_name:
            return None

        # Fetch the target document that is handling this reference.
        comp: Component = components[real_parent_name]

        # Fetch the source of our component
        source = comp_doc.get(comp.name)
        if not source:
            return None

        # Fetch the docname of the target component
        target_doc = comp_doc.get(comp.name)
        if not target_doc:
            return None

        # Extract the missing part
        remainder = target_slug[len(parent_slug) :].strip("-")  # type: ignore

        # Now, we can search for the right module name.
        # This has an effect : Will always match the first element in case multiple elements are assigned.
        # This is fine as it's a backup.
        module_name = ""
        for module in comp.modules:
            if target_slug.startswith(module.entity.replace("_", "-")):
                module_name = module.name
                break

        # Build the missing reference.
        # Try to link to ourselves, but will default to the generic module element.
        if module_name:
            target_anchor = make_id(f"{parent_slug}-module-{module_name}")
        else:
            target_anchor = make_id(f"{parent_slug}-module")

        # Build the URI ...
        base_uri = builder.get_relative_uri(fromdocname, target_doc)

        ref_node = nodes.reference(
            "",
            "",
            internal=True,
            refuri=f"{base_uri}#{target_anchor}",
            classes=["rtl-fallback-instance-xref"],
        )
        ref_node += contnode
        return ref_node
