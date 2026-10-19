# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    18/09/2026
#
# Brief :   Define the queries used by the VHDL parser.
# ----------------------------------------------------------------------------

# From
import tree_sitter_vhdl as tsvhdl
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
            """,
        ),
        "Q_PORTS": Query(
            lang,
            """
            (entity_declaration
                (identifier) @entity.name
                (port_clause
                    (interface_list
                    (interface_declaration
                        (identifier_list) @port.ids
                        (simple_mode_indication
                            (mode)? @port.mode
                            (subtype_indication) @port.subtype))))?
            ) @entity.node
            """,
        ),
        "Q_TYPES": Query(
            lang,
            """
            (type_declaration
                (identifier) @type.name
                (enumeration_type_definition) @type.enum)
        
            (type_declaration
                (identifier) @type.name
                (record_type_definition) @type.struct)

            (type_declaration
                (identifier) @type.name
                (array_type_definition) @type.array)
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
                (label_declaration (label))? @process.label) @process.node
            """,
        ),
        "Q_ASSIGNS": Query(
            lang,
            """
            (concurrent_simple_signal_assignment) @assign.concurrent
                (concurrent_conditional_signal_assignment) @assign.conditional
            """,
        ),
        "Q_MODULES": Query(
            lang,
            """
            (component_instantiation_statement
                (label_declaration (label))? @inst.label
                (name) @inst.type) @inst.node
            """,
        ),
        "Q_FUNCTIONS": Query(
            lang,
            """
            (function_specification
                (identifier) @func.name) @func.node

            (procedure_specification
                (identifier) @proc.name) @proc.node
            """,
        ),
        "Q_GENERATES": Query(
            lang,
            """
            (generate_body) @gen.node
                (case_generate_body) @gen.node
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
