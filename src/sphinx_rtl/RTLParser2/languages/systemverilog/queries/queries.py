# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the queries used by the Verilog parser.
# ----------------------------------------------------------------------------

# From
from tree_sitter import Language, Query


def get_queries(lang: Language) -> dict[str, Query]:
    """
    Build the queries for the passed language.
    """

    # "Q_INTERFACES"
    # "Q_MODPORTS"
    # "Q_PARAMETERS"
    # "Q_PORTS"
    # "Q_PROCESS"
    # "Q_FUNCTIONS"
    # "Q_SIGNALS"
    # "Q_STRUCTURES"

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
            (module_declaration
                (module_header
                    [
                        (simple_identifier)
                        (escaped_identifier)
                    ] @module.name
                ) @entity.node
            )
            """,
        ),
        "Q_MODULES": Query(
            lang,
            """
            (_
                [
                    (simple_identifier)
                    (escaped_identifier)
                    (interface_identifier)
                    (program_identifier)
                    (checker_identifier)
                ] @module.instance.type
                (parameter_value_assignment)? @module.parameters
                (hierarchical_instance
                    (name_of_instance) @module.instance.name
                    (list_of_port_connections)? @ports.list
                ) @module.instance
            ) @module.node
            """,
        ),
        "Q_ASSIGNS": Query(
            lang,
            """
            (continuous_assign
                [
                    (list_of_net_assignments
                        (net_assignment
                            (net_lvalue) @assign.target
                            (expression) @assign.source
                        )*
                    )
                    (list_of_variable_assignments
                        (variable_assignment
                            (variable_lvalue) @assign.target
                            (expression) @assign.source
                        )*
                    )
                ]
            ) @assign.node
            """,
        ),
        "Q_IMPORTS": Query(
            lang,
            """
            (package_import_item
                (package_identifier) @import.identifier
                [
                    (_) @import.element
                ]
            ) @import
            """,
        ),
        "Q_ENUM": Query(
            lang,
            """
           (type_declaration
                (data_type) @typedef.body
                [
                    (simple_identifier)
                    (escaped_identifier)
                ] @typedef.name
            ) @typedef.node
            """,
        ),
    }
