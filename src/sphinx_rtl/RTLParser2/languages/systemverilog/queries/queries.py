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
    # "Q_PROCESS"
    # "Q_FUNCTIONS"

    return {
        "Q_COMMENTS": Query(lang, """(comment) @comment"""),
        "Q_PORTS": Query(
            lang,
            """
            (port_declaration
                (attribute_instance)? @port.instance
                [
                    (inout_declaration) @port.inout
                    (input_declaration) @port.input
                    (output_declaration) @port.output
                    (ref_declaration) @port.ref
                    (interface_port_declaration) @port.interface
                ] @port.direction
            ) @port.node

            (ansi_port_declaration
                [
                    (net_port_header1) @port.net
                    (interface_port_header) @port.interface
                    (variable_port_header) @port.var
                ]?
                [
                    (port_identifier)
                    (simple_identifier)
                    (escaped_identifier)
                ] @port.name
            ) @port.node
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
        # Q_ENUM also handle Q_STRUCTURES !
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
        "Q_PARAMETERS": Query(
            lang,
            """
            (parameter_declaration
                (data_type_or_implicit1)? @parameter.type
                [
                    (list_of_param_assignments) @parameter.elements
                    (list_of_type_assignments) @parameter.elements
                ]
            ) @parameter.node

            (local_parameter_declaration
                (data_type_or_implicit1)? @parameter.type
                [
                    (list_of_param_assignments) @parameter.elements
                    (list_of_type_assignments) @parameter.elements      
                ]
            ) @parameter.node
            """,
        ),
        "Q_SIGNALS": Query(
            lang,
            """
            [
                (net_declaration
                    [
                        (
                            (net_type)? @signal.kind
                            (data_type_or_implicit1)? @signal.type
                            (list_of_net_decl_assignments) @signal.names
                        )
                        (
                            [
                                (simple_identifier)
                                (escaped_identifier) 
                            ] @signal.type
                            (list_of_net_decl_assignments) @signal.names
                        )
                    ]
                ) @signal.node

                (data_declaration
                    [
                        (
                            (data_type_or_implicit1)? @signal.type
                            (list_of_variable_decl_assignments) @signal.names
                        )
                        (type_declaration) @signal.type
                        (net_type_declaration) @signal.type
                    ]
                ) @signal.node
            ]
            """,
        ),
    }
