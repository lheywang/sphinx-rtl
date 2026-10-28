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
# PORTS
# -----------------------------------------------------------
PORTS_ANSI_NET_Q = Query(
    VERILOG_LANGUAGE,
    """
    (net_port_header1
        [
            (
                (port_direction)? @direction
                (net_port_type1) @type
            )
            (port_direction) @direction
        ]
    )
    """,
)

PORTS_ANSI_INTERFACE_Q = Query(
    VERILOG_LANGUAGE,
    """
    (interface_port_header
        (interface_identifier)? @type
        (modport_identifier) @direction
    )
    """,
)

PORTS_ANSI_VARIABLE_Q = Query(
    VERILOG_LANGUAGE,
    """
    (variable_port_header
        (port_direction)? @direction
        (
            [
                (data_type)
                (data_type_or_implicit1) 
            ] @type
        )
    )
    """,
)

PORTS_NON_ANSI_INOUT_Q = Query(
    VERILOG_LANGUAGE,
    """
    (inout_declaration
        (net_port_type1)? @port.type
        (list_of_port_identifiers
            (port_identifier) @port.name
            (unpacked_dimension) @port.dimension
        )  
    ) @port.direction
    """,
)

PORTS_NON_ANSI_INPUT_OUTPUT_Q = Query(
    VERILOG_LANGUAGE,
    """
    (input_declaration
        [
            (net_port_type1)
            (data_type)
            (_)
        ]? @port.type
        [
            (list_of_port_identifiers
                [
                    (port_identifier)
                    (simple_identifier)
                    (escaped_identifier)
                ] @port.name
            )
            (list_of_variable_identifiers
                [
                    (simple_identifier)
                    (escaped_identifier)
                ] @port.name
            )
            (list_of_variable_port_identifiers
                [
                    (port_identifier)
                    (simple_identifier)
                    (escaped_identifier)
                ] @port.name
            )
        ]
        (unpacked_dimension)? @port.dimension
    ) @port.direction

    (output_declaration
        [
            (net_port_type1)
            (data_type)
            (_)
        ]? @port.type
        [
            (list_of_port_identifiers
                [
                    (port_identifier)
                    (simple_identifier)
                    (escaped_identifier)
                ] @port.name
            )
            (list_of_variable_identifiers
                [
                    (simple_identifier)
                    (escaped_identifier)
                ] @port.name
            )
            (list_of_variable_port_identifiers
                [
                    (port_identifier)
                    (simple_identifier)
                    (escaped_identifier)
                ] @port.name
            )
        ]
        (unpacked_dimension)? @port.dimension
    ) @port.direction
    """,
)

PORTS_NON_ANSI_REF_Q = Query(
    VERILOG_LANGUAGE,
    """
    (ref_declaration
        [
            (_)
        ] @port.type
        (list_of_variable_identifiers
            [
                (simple_identifier)
                (escaped_identifier)
            ] @port.name
            [
                (unsized_dimension)
                (unpacked_dimension)
                (associative_dimension)
                (queue_dimension)    
            ] @port.dimension
        )
    ) @port.direction
    """,
)

PORTS_NON_ANSI_INTERFACE_Q = Query(
    VERILOG_LANGUAGE,
    """
    (interface_port_declaration
        (interface_identifier) @port.type
        (modport_identifier) @port.direction
        (list_of_interface_identifiers
            (unpacked_dimension) @port.dimension
        )
    )
    """,
)

# -----------------------------------------------------------
# PARAMETERS
# -----------------------------------------------------------
PARAMS_ELEMENTS_Q = Query(
    VERILOG_LANGUAGE,
    """
    (param_assignment
        (parameter_identifier) @parameter.identifier
        (unpacked_dimension)?* @parameter.dimensions
        (constant_param_expression
            [
                (constant_mintypmax_expression)? @parameter.value
                (data_type)? @parameter.type
            ] 
        )
    ) @parameter

    (type_assignment
        [
            (simple_identifier) @parameter.type
            (escaped_identifier) @parameter.type
        ]
        (data_type)? @parameter.type
    
    ) @parameter    
    """,
)

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
