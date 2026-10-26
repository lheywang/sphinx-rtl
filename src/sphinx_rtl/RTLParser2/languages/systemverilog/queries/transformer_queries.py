# ----------------------------------------------------------------------------
# Author :  l.heywang <leonard.heywang@proton.me>
# Date :    26/09/2026
#
# Brief :   Define the queries used by the different parsers to dig
#           deeper in the AST.
#           Compared to the ones in the queries.py file, they aren't
#           called by the central parser.
# ----------------------------------------------------------------------------

# Imports
import tree_sitter_verilog

from tree_sitter import Language, Query

# As we use our own language, let's define it
VERILOG_LANGUAGE = Language(tree_sitter_verilog.language())

# -----------------------------------------------------------
# MODULES
# -----------------------------------------------------------
MODULE_PORT_Q = Query(
    VERILOG_LANGUAGE,
    """
    (named_port_connection
        (port_identifier) @name
        (expression)? @value) @conn
    (ordered_port_connection
        (expression) @value) @conn
""",
)

MODULE_PARAM_Q = Query(
    VERILOG_LANGUAGE,
    """
    (named_parameter_assignment
        (parameter_identifier) @name
        (param_expression)? @value) @conn
    (ordered_parameter_assignment
        (_)? @value) @conn
""",
)
MODULE_LOOP_Q = Query(
    VERILOG_LANGUAGE,
    """
    (loop_generate_construct
        (genvar_initialization) @init
        (constant_expression)   @cond
        (genvar_iteration)      @step) @gen
""",
)

MODULE_IF_Q = Query(
    VERILOG_LANGUAGE,
    """
    (if_generate_construct
        (constant_expression) @cond) @gen
""",
)

MODULE_CASE_Q = Query(
    VERILOG_LANGUAGE,
    """
    (case_generate_construct
        (constant_expression) @cond) @gen
""",
)

# -----------------------------------------------------------
# ENUMS
# -----------------------------------------------------------
ENUM_Q_MEMBERS = Query(
    VERILOG_LANGUAGE,
    """
    (struct_union_member
        (data_type_or_void) @member.type
        (list_of_variable_decl_assignments
            (variable_decl_assignment
                [
                    (simple_identifier)
                    (escaped_identifier)
                ] @member.name
                (expression)? @member.value
            )
        )
    )

    (enum_name_declaration
        (enum_identifier) @enum.item
        (constant_expression)? @enum.value
    )
    """,
)
