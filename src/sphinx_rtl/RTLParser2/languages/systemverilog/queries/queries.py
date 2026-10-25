# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the queries used by the VHDL parser.
# ----------------------------------------------------------------------------

# From
from tree_sitter import Language, Query


def get_queries(lang: Language) -> dict[str, Query]:
    """
    Build the queries for the passed language.
    """

    return {
        "Q_COMMENTS": Query(lang, """(comment) @comment"""),
        "Q_PORTS": Query(
            lang,
            """
            (port) @port
            """,
        ),
        "Q_ENTITIES": Query(
            lang,
            """
            (module_declaration) @entity.node
            """,
        ),
    }
