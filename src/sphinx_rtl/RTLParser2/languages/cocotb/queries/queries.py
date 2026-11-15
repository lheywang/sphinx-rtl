# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    15/11/2026
#
# Brief :   Define the queries used by the Cocotb parser.
# ----------------------------------------------------------------------------

# From
from tree_sitter import Language, Query


def get_queries(lang: Language) -> dict[str, Query]:
    """
    Build the queries for the passed language.
    """

    return {
        "Q_ENTITIES": Query(lang, "(module)"),
        "Q_COMMENTS": Query(
            lang,
            """
            (comment) @comment
            (module
                . (expression_statement
                    (string) @comment
                )
            )
            (function_definition
                body: (block
                    . (expression_statement
                        (string) @comment    
                    )
                )
            )
            """,
        ),
        "Q_IMPORTS": Query(
            lang,
            """
            (import_statement
                name: [
                    (dotted_name) @import
                    (aliased_import
                        name: (dotted_name) @import
                        alias: (identifier) @alias
                    ) 
                ]
            )

            (import_from_statement
                module_name: [
                    (dotted_name) @import
                    (relative_import) @import
                ]
            )
            """,
        ),
        "Q_PARAMETERS": Query(
            lang,
            """
            (module
                (expression_statement
                    (assignment
                        left: (identifier) @name
                        type: (type)? @type
                        right: (_)? @value
                        (#match? @name "^[A-Z][A-Z0-9_]*$")
                    )
                )
            )
            """,
        ),
        "Q_PROCESS": Query(
            lang,
            """
            (decorated_definition
                (decorator
                    [
                        (attribute
                            object: (identifier) @pkg
                            attribute: (identifier) @dec
                        )
                        (call
                            function: (attribute
                                object: (identifier) @pkg
                                attribute: (identifier) @dec
                            )
                        )
                    ]
                    (#eq? @pkg "cocotb")
                    (#eq? @dec "test")
                )
                definition: (function_definition
                    name: (identifier) @name
                )
            )
            """,
        ),
    }
