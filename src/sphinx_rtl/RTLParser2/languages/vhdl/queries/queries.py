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
        "Q_COMMENTS": Query(
            lang,
            """
            (line_comment (comment_content) @content) @node
            """,
        ),
        "Q_IMPORTS": Query(
            lang,
            """
            (library_clause (logical_name_list) @import.lib)
                (use_clause (selected_name_list) @import.use)
            """,
        ),
        "Q_PARAMETERS": Query(
            lang,
            """
            (generic_clause
                (interface_list
                    (interface_declaration
                        (identifier_list) @param.ids
                        (simple_mode_indication
                        (subtype_indication) @param.subtype
                        (initialiser)? @param.init))))

            (constant_declaration
                (identifier_list) @constant.names
                (subtype_indication) @constant.type
                (initialiser)? @constant.init
            ) @constant.node
            """,
        ),
        "Q_PORTS": Query(
            lang,
            """
            (port_clause
                (interface_list
                    [
                    (interface_declaration
                        (identifier_list) @port.ids
                        (simple_mode_indication
                            (mode)? @port.mode
                            (subtype_indication) @port.subtype
                        )
                    )
                    (interface_signal_declaration
                        (identifier_list) @port.ids
                        (simple_mode_indication
                            (mode)? @port.mode
                            (subtype_indication) @port.subtype
                        )
                    )
                    ]
                )
            )
            """,
        ),
        "Q_TYPES": Query(
            lang,
            """
            (type_declaration
                (identifier) @type.name
                [
                    (array_type_definition) @type.array
                    (enumeration_type_definition) @type.enum
                    (record_type_definition
                        (element_declaration
                            (identifier_list) @record.field.ids
                            (subtype_indication) @record.field.type
                        )+ @type.fields
                    ) @type.record
                ]?
            )
            """,
        ),
        "Q_SIGNALS": Query(
            lang,
            """
            (signal_declaration
                (identifier_list) @signal.ids
                (subtype_indication) @signal.subtype
                (initialiser)? @signal.init)
            """,
        ),
        "Q_PROCESSES": Query(
            lang,
            """
            (process_statement
                (label_declaration
                    (label) @process.label
                )?
                (sensitivity_specification
                    (sensitivity_list)? @process.sensitivity
                )?
                (sequential_block) @process.body
            ) @process.node
            """,
        ),
        "Q_ASSIGNS": Query(
            lang,
            """
            (concurrent_simple_signal_assignment
                (name) @assign.target
                (waveform) @assign.waveform
            ) @assign.concurrent

            (concurrent_conditional_signal_assignment
                (name) @assign.target
                (conditional_waveforms) @assign.waveform
            ) @assign.conditional
            """,
        ),
        "Q_MODULES": Query(
            lang,
            """
            (component_instantiation_statement
                (label_declaration) @inst.unit.label
                (instantiated_unit)? @inst.unit.unit
                (name)? @inst.unit.name

                (generic_map_aspect
                    (association_list) @inst.generics
                )?

                (port_map_aspect
                    (association_list) @inst.ports
                )?
            )@inst.unit
            """,
        ),
        "Q_FUNCTIONS": Query(
            lang,
            """
            (function_specification
                (identifier) @func.name
                (subprogram_header)? @func.header
                (parameter_list_specification) @func.args
                (name) @func.return
            ) @func.node

            (procedure_specification
                (identifier) @proc.name
                (subprogram_header)? @func.header
                (parameter_list_specification) @func.args
            ) @proc.node
            """,
        ),
        "Q_ENTITY": Query(
            lang,
            """
            (entity_declaration
                (identifier) @entity.name
            ) @entity.node 
            """,
        ),
    }
