# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    25/09/2026
#
# Brief :   Extract all the imports from a module
# ----------------------------------------------------------------------------

# Imports
import pyslang.syntax as syntax
from pyslang import SourceManager

from ...models import Import


def _parse_import_declaration(
    decl: syntax.PackageImportDeclarationSyntax, sm: SourceManager
) -> list[Import]:
    results = []
    for item in decl.items:
        pkg_name = str(item.package).strip()
        item_name = str(item.item).strip() if item.item else "*"

        line = sm.getLineNumber(item.package.location)
        if line == 0:
            line = -1

        results.append(Import(library=pkg_name, element=[item_name], line=line))
    return results


def extract_imports(tree: syntax.SyntaxTree, sm: SourceManager) -> list[Import]:
    imports: list[Import] = []

    # Extract all the elements :
    for member in tree.root.members:  # type: ignore
        if isinstance(member, syntax.PackageImportDeclarationSyntax):
            imports.extend(_parse_import_declaration(member, sm))

        elif hasattr(member, "members"):
            for sub_member in member.members:
                if isinstance(sub_member, syntax.PackageImportDeclarationSyntax):
                    imports.extend(_parse_import_declaration(sub_member, sm))

    # Reduce the imports
    lib_names: list[str] = []
    reduced_imports: list[Import] = []
    for imported in imports:
        if imported.library not in lib_names:
            lib_names.append(imported.library)
            reduced_imports.append(imported)
        else:
            for reduced_import in reduced_imports:
                if imported.library == reduced_import.library:
                    reduced_import.element.extend(imported.element)

    return reduced_imports
