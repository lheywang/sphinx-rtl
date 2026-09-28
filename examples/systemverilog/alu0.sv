/*
 *  Define the ALU0 module. Able to operate on the most basic operands.
 *
 *  Know ADD, SUB, AND, OR, XOR bit operations. Can't do anything more.
 *  Use the others ALUs for a full coverage of the operations.
 *
 *  @clock master 100MHz clk
 *  @target Altera MAX10
 *  @target Quartus 24.1
 *  @sim Verilator
 */

`timescale 1ns / 1ps

import core_config_pkg::XLEN;
import core_config_pkg::alu_commands_t;
import core_config_pkg::REG_i_addr_W;

module alu0 #(
    parameter ENABLE_SINGLE_CYCLE = 0,
    parameter ENABLE_OUTPUT_REGISTERS = 1
) (
    input  logic                                                    clk,        // **Master clock** input
    input  logic                                                    rst_n,      // **Master o_reset** input
    input  logic          [      (core_config_pkg::XLEN - 1) : 0]   i_arg0,     // Operand A
    input  logic          [      (core_config_pkg::XLEN - 1) : 0]   i_arg1,     // Operand B
    input  logic          [      (core_config_pkg::XLEN - 1) : 0]   i_addr,     // Target address (unused)
    input  logic          [      (core_config_pkg::XLEN - 1) : 0]   i_imm,      // immediate value
    input  alu_commands_t                                           i_cmd,      // Decoded opcode
    input  logic          [(core_config_pkg::REG_i_addr_W - 1) : 0] i_rd,       // Target register
    output logic                                                    i_busy,     // busy flag. This alu never assert it.
    output logic                                                    i_error,    // Error input
    output logic          [      (core_config_pkg::XLEN - 1) : 0]   o_res,      // o_result value
    output logic          [      (core_config_pkg::XLEN - 1) : 0]   o_jmp,      // Does a jump is needed ?
    output logic          [(core_config_pkg::REG_i_addr_W - 1) : 0] o_rd,       // Output register
    output logic                                                    o_valid,    // o_valid output bit
    output logic                                                    o_error,    // Output error code.
    output logic                                                    o_req,      // Output o_request
    input  logic                                                    o_clear,    // Output o_clear
    axi4_stream.source                                              stream      // AXI4-ST Stream to another ALU.
);
    /*
     *  Storages types
     */
    logic [(core_config_pkg::XLEN) : 0] tmp_o_res;  // One more bit to handle overflow.
    logic                               unknown_instr;
    logic                               int_o_req;
    logic                               end_of_op;

    /*
     *  First, perform calculations (outputs from issuer are synchronous to clock).
     */
    always_comb begin

        unique case (i_cmd)

            core_config_pkg::c_ADD: begin
                // Calculation
                tmp_o_res       = {1'b0, i_arg0} + {1'b0, i_arg1};

                // Setting flags
                int_o_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_SUB: begin
                // Calculation
                tmp_o_res       = {1'b0, i_arg0} - {1'b0, i_arg1};

                // Setting flags
                int_o_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_AND: begin
                // Calculation
                tmp_o_res       = {1'b0, i_arg0} & {1'b0, i_arg1};

                // Setting flags
                int_o_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_OR: begin
                // Calculation
                tmp_o_res       = {1'b0, i_arg0} | {1'b0, i_arg1};

                // Setting flags
                int_o_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            core_config_pkg::c_XOR: begin
                // Calculation
                tmp_o_res       = {1'b0, i_arg0} ^ {1'b0, i_arg1};

                // Setting flags
                int_o_req       = 1'b1;
                unknown_instr = 1'b0;
            end
            default: begin
                // Calculation
                tmp_o_res       = 33'b0;

                // Setting flags
                int_o_req       = 1'b0;
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

            i_busy      <= 1'b0;
            o_res       <= 32'b0;
            i_error   <= 1'b0;
            o_error   <= 1'b0;
            o_req       <= 1'b0;
            o_rd      <= 5'b0;
            o_valid     <= 1'b0;
            end_of_op <= 1'b0;

        end else if (o_clear && end_of_op) begin

            i_busy      <= 1'b0;
            o_res       <= 32'b0;
            i_error   <= 1'b0;
            o_error   <= 1'b0;
            o_req       <= 1'b0;
            o_rd      <= 5'b0;
            o_valid     <= 1'b0;
            end_of_op <= 1'b0;

        end else begin

            i_busy      <= int_o_req;
            o_res       <= tmp_o_res[(core_config_pkg::XLEN-1) : 0];
            i_error   <= unknown_instr;
            o_error   <= tmp_o_res[(core_config_pkg::XLEN)];
            o_req       <= 1'b0;
            o_rd      <= i_rd;
            o_valid     <= 1'b1;
            end_of_op <= 1'b1;

        end
    end
endmodule