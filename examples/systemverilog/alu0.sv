/*
 *  Define the ALU0 module. Able to operate on the most basic operands.
 *
 *  Know ADD, SUB, AND, OR, XOR bit operations. Can't do anything more.
 *  Use the others ALUs for a full coverage of the operations.
 */

`timescale 1ns / 1ps

import core_config_pkg::XLEN;
import core_config_pkg::alu_commands_t;
import core_config_pkg::REG_ADDR_W;

module alu0 #(
    parameter ENABLE_SINGLE_CYCLE = 0,
    parameter ENABLE_OUTPUT_REGISTERS = 1
) (
    input  logic                                                  clk,      // **Master clock** input
    input  logic                                                  rst_n,    // **Master reset** input
    input  logic          [      (core_config_pkg::XLEN - 1) : 0] arg0,     // Operand A
    input  logic          [      (core_config_pkg::XLEN - 1) : 0] arg1,     // Operand B
    input  logic          [      (core_config_pkg::XLEN - 1) : 0] addr,     // Target address (unused)
    input  logic          [      (core_config_pkg::XLEN - 1) : 0] imm,      // Immediate value
    input  alu_commands_t                                         cmd,      // Decoded opcode
    input  logic          [(core_config_pkg::REG_ADDR_W - 1) : 0] i_rd,     // Target register
    output logic                                                  busy,     // Busy flag. This alu never assert it.
    output logic                                                  i_error,  // Error input
    output logic          [      (core_config_pkg::XLEN - 1) : 0] res,      // Result value
    output logic          [      (core_config_pkg::XLEN - 1) : 0] jmp,      // Does a jump is needed ?
    output logic          [(core_config_pkg::REG_ADDR_W - 1) : 0] o_rd,     // Output register
    output logic                                                  valid,    // Valid output bit
    output logic                                                  o_error,  // Output error code.
    output logic                                                  req,      // Output request
    input  logic                                                  clear,    // Output clear
    axi4_stream.source                                            stream    // AXI4-ST Stream to another ALU.
);
    /*
     *  Storages types
     */
    logic [(core_config_pkg::XLEN) : 0] tmp_res;  // One more bit to handle overflow.
    logic                               unknown_instr;
    logic                               int_req;
    logic                               end_of_op;

    /*
     *  First, perform calculations (outputs from issuer are synchronous to clock).
     */
    always_comb begin

        unique case (cmd)

            core_config_pkg::c_ADD: begin
                // Calculation
                tmp_res       = {1'b0, arg0} + {1'b0, arg1};

                // Setting flags
                int_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_SUB: begin
                // Calculation
                tmp_res       = {1'b0, arg0} - {1'b0, arg1};

                // Setting flags
                int_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_AND: begin
                // Calculation
                tmp_res       = {1'b0, arg0} & {1'b0, arg1};

                // Setting flags
                int_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_OR: begin
                // Calculation
                tmp_res       = {1'b0, arg0} | {1'b0, arg1};

                // Setting flags
                int_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_XOR: begin
                // Calculation
                tmp_res       = {1'b0, arg0} ^ {1'b0, arg1};

                // Setting flags
                int_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            default: begin
                // Calculation
                tmp_res       = 33'b0;

                // Setting flags
                int_req       = 1'b0;
                unknown_instr = 1'b1;
            end
        endcase
    end

    /*
     *  Second, latching the first stage outputs before outputing them for the
     *  commiter stage.
     */
    always_ff @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin

            busy      <= 1'b0;
            res       <= 32'b0;
            i_error   <= 1'b0;
            o_error   <= 1'b0;
            req       <= 1'b0;
            o_rd      <= 5'b0;
            valid     <= 1'b0;
            end_of_op <= 1'b0;

        end else if (clear && end_of_op) begin

            busy      <= 1'b0;
            res       <= 32'b0;
            i_error   <= 1'b0;
            o_error   <= 1'b0;
            req       <= 1'b0;
            o_rd      <= 5'b0;
            valid     <= 1'b0;
            end_of_op <= 1'b0;

        end else begin

            busy      <= int_req;
            res       <= tmp_res[(core_config_pkg::XLEN-1) : 0];
            i_error   <= unknown_instr;
            o_error   <= tmp_res[(core_config_pkg::XLEN)];
            req       <= 1'b0;
            o_rd      <= i_rd;
            valid     <= 1'b1;
            end_of_op <= 1'b1;

        end
    end
endmodule