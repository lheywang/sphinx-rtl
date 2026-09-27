/*
 *  File :      rtl/core/assembly/assembly_alu.sv
 *
 *  Author :    l.heywang <leonard.heywang@proton.me>
 *  Date :      25/10.2025
 *  
 *  Brief :     This file assemble all of the ALU with the issuer
 *              and commiter units. This is done to make the global
 *              core.sv file much more readable.
 *
 *  Note :      There's not associated testbench for this module.
 */

import core_config_pkg::XLEN;
import core_config_pkg::REG_ADDR_W;
import core_config_pkg::CSR_ADDR_W;
import core_config_pkg::alu_commands_t;

module assembly_alu #(
        parameter int ENABLE_CSR = 1
    ) (

    input logic clk,
    input logic clk_en,
    input logic rst_n,

    // From decoder
    input  logic     [(REG_ADDR_W - 1) : 0] rs1,
    input  logic     [(REG_ADDR_W - 1) : 0] rs2,
    input  logic     [(REG_ADDR_W - 1) : 0] rd,
    input  logic     [      (XLEN - 1) : 0] imm,
    input  logic     [      (XLEN - 1) : 0] address,
    input  opcodes_t                        opcode,
    input  logic                            illegal,
    output logic                            busy,
    output logic                            flush,
    input  logic                            branch_taken,
    input  logic                            count_decoded,

    // Output logic
    output logic PC_en,
    output logic PC_load,
    output logic [(XLEN - 1) : 0] PC_addr,
    input logic PC_ovf,

    // memory interface
    output logic [      (XLEN - 1) : 0] mem_addr,
    output logic [((XLEN / 8) - 1) : 0] mem_byteen,
    output logic                        mem_we,
    output logic                        mem_req,
    output logic [      (XLEN - 1) : 0] mem_wdata,
    input  logic [      (XLEN - 1) : 0] mem_rdata,
    input  logic                        mem_err,

    // Branch prediction feedback
    output logic bpu_branch_taken,
    output logic bpu_branch_not_taken,

    // Interrupts vector
    input logic [(core_config_pkg::XLEN - 1) : 0] interrupt_vect

);

    /*
     *  Issuer <-> Registers
     */
    logic          [(REG_ADDR_W - 1) : 0] reg_ra0;
    logic          [(REG_ADDR_W - 1) : 0] reg_ra1;
    logic          [      (XLEN - 1) : 0] reg_rd0;
    logic          [      (XLEN - 1) : 0] reg_rd1;

    /*
      * Issuer <-> Occupancy
      */
    logic          [(REG_ADDR_W - 1) : 0] occupancy_rd;
    logic          [(REG_ADDR_W - 1) : 0] occupancy_rs1;
    logic          [(REG_ADDR_W - 1) : 0] occupancy_rs2;
    logic                                 occupancy_exec;
    logic                                 occupancy_lock;

    /*
      * Issuer <-> ALUs
      */
    logic          [      (XLEN - 1) : 0][4:0] alu0_arg0;
    logic          [      (XLEN - 1) : 0][4:0] alu0_arg1;
    logic          [      (XLEN - 1) : 0][4:0] alu0_addr;
    logic          [      (XLEN - 1) : 0][4:0] alu0_imm;
    alu_commands_t                       [4:0] alu0_cmd;
    logic          [(REG_ADDR_W - 1) : 0][4:0] alu0_i_rd;
    logic                                [4:0] alu0_busy;
    logic                                [4:0] alu0_i_error;

    /*
     *  ALUs <-> Commiter
     */
    logic                                [4:0] alu0_o_error;
    logic                                [4:0] alu0_valid;
    logic                                [4:0] alu0_req;
    logic          [      (XLEN - 1) : 0][4:0] alu0_res;
    logic          [      (XLEN - 1) : 0][4:0] alu0_jmp;
    logic          [(REG_ADDR_W - 1) : 0][4:0] alu0_o_rd;
    logic                                [4:0] alu0_clear;

    /*
     *  Commiter <-> Registers
     */
    logic          [      (XLEN - 1) : 0] reg_data;
    logic          [(REG_ADDR_W - 1) : 0] reg_addr;
    logic                                 reg_we;

    /*
     *  Commiter <-> Issuer
     */
    logic                                 int_flush;
    logic                                 halt_needed;
    logic                                 commit_err;

    /*
     *  ALU 4 <-> CSR
     */
    logic          [(CSR_ADDR_W - 1) : 0] csr_wa;
    logic          [(CSR_ADDR_W - 1) : 0] csr_ra;
    logic                                 csr_we;
    logic          [      (XLEN - 1) : 0] csr_wd;
    logic          [      (XLEN - 1) : 0] csr_rd;
    logic                                 csr_err;

    /*
     *  CSR <-> Issuer
     */
    logic                                 halt_pend;

    /*
     *  Instiating the issuer module
     */
    issuer issuer (
        .clk  (clk),
        .rst_n(rst_n),

        .dec_rs1(rs1),
        .dec_rs2(rs2),
        .dec_rd(rd),
        .dec_imm(imm),
        .dec_address(address),
        .dec_opcode(opcode),
        .dec_illegal(illegal),
        .dec_branch_taken(branch_taken),
        .dec_busy(busy),
        .dec_flush(flush),

        .occupancy_lock(occupancy_lock),
        .occupancy_exec(occupancy_exec),
        .occupancy_rd  (occupancy_rd),
        .occupancy_rs1 (occupancy_rs1),
        .occupancy_rs2 (occupancy_rs2),

        .reg_ra0(reg_ra0),
        .reg_ra1(reg_ra1),
        .reg_rd0(reg_rd0),
        .reg_rd1(reg_rd1),

        .alu0_arg0(alu0_arg0),
        .alu0_arg1(alu0_arg1),
        .alu0_addr(alu0_addr),
        .alu0_imm(alu0_imm),
        .alu0_cmd(alu0_cmd),
        .alu0_rd(alu0_i_rd),
        .alu0_busy(alu0_busy),
        .alu0_error(alu0_i_error),

        .alu1_arg0(alu1_arg0),
        .alu1_arg1(alu1_arg1),
        .alu1_addr(alu1_addr),
        .alu1_imm(alu1_imm),
        .alu1_cmd(alu1_cmd),
        .alu1_rd(alu1_i_rd),
        .alu1_busy(alu1_busy),
        .alu1_error(alu1_i_error),
        .alu1_predict_in(alu1_predict_in),

        .alu2_arg0(alu2_arg0),
        .alu2_arg1(alu2_arg1),
        .alu2_addr(alu2_addr),
        .alu2_imm(alu2_imm),
        .alu2_cmd(alu2_cmd),
        .alu2_rd(alu2_i_rd),
        .alu2_busy(alu2_busy),
        .alu2_error(alu2_i_error),

        .alu3_arg0(alu3_arg0),
        .alu3_arg1(alu3_arg1),
        .alu3_addr(alu3_addr),
        .alu3_imm(alu3_imm),
        .alu3_cmd(alu3_cmd),
        .alu3_rd(alu3_i_rd),
        .alu3_busy(alu3_busy),
        .alu3_error(alu3_i_error),

        .alu4_arg0(alu4_arg0),
        .alu4_arg1(alu4_arg1),
        .alu4_addr(alu4_addr),
        .alu4_imm(alu4_imm),
        .alu4_cmd(alu4_cmd),
        .alu4_rd(alu4_i_rd),
        .alu4_busy(alu4_busy),
        .alu4_error(alu4_i_error),

        .alu5_arg0(alu5_arg0),
        .alu5_arg1(alu5_arg1),
        .alu5_addr(alu5_addr),
        .alu5_imm(alu5_imm),
        .alu5_cmd(alu5_cmd),
        .alu5_rd(alu5_i_rd),
        .alu5_busy(alu5_busy),
        .alu5_error(alu5_i_error),

        .halt_needed (halt_needed),
        .flush_needed(int_flush),

        .halt_pending(halt_pend),
        .commit_err(commit_err),
        .PC_ovf(PC_ovf)
    );

    /*
     *  Instantiating the external, common elements (registers (STD and CSR) + occupancy trackers)
     */
    registers registers (
        .clk(clk),
        .we (reg_we),
        .wa (reg_addr),
        .wd (reg_data),
        .ra1(reg_ra0),
        .ra2(reg_ra1),
        .rd1(reg_rd0),
        .rd2(reg_rd1)
    );

    occupancy occup (
        clk,
        rst_n,
        occupancy_rd,
        occupancy_rs1,
        occupancy_rs2,
        occupancy_exec,
        occupancy_lock,
        reg_addr,
        reg_we
    );

    generate
        if (ENABLE_CSR) begin : gen_optional_pipe
            assembly_csr csrs (
                .clk(clk),
                .clk_en(clk_en),
                .rst_n(rst_n),
                .csr_wa(csr_wa),
                .csr_ra(csr_ra),
                .csr_we(csr_we),
                .csr_wd(csr_wd),
                .csr_rd(csr_rd),
                .csr_err(csr_err),
                .count_waited(1'b1),
                .count_decoded(count_decoded),
                .count_flushed(1'b1),
                .count_commited(1'b1),
                .halt_pending(halt_pend),
                .interrupt_vect(interrupt_vect)
            );

            assembly_csr csrs2 (
                .clk(clk),
                .clk_en(clk_en),
                .rst_n(rst_n),
                .csr_wa(csr_wa),
                .csr_ra(csr_ra),
                .csr_we(csr_we),
                .csr_wd(csr_wd),
                .csr_rd(csr_rd),
                .csr_err(csr_err),
                .count_waited(1'b1),
                .count_decoded(count_decoded),
                .count_flushed(1'b1),
                .count_commited(1'b1),
                .halt_pending(halt_pend),
                .interrupt_vect(interrupt_vect)
            );
        end
    endgenerate

    /*
     *  Instantianting the ALUs
     */
    alu0 alu_0 [4:0] (
        .clk(clk),
        .rst_n(rst_n),
        .arg0(alu0_arg0),
        .arg1(alu0_arg1),
        .addr(alu0_addr),
        .imm(alu0_imm),
        .cmd(alu0_cmd),
        .i_rd(alu0_i_rd),
        .busy(alu0_busy),
        .i_error(alu0_i_error),
        .res(alu0_res),
        .jmp(alu0_jmp),
        .o_rd(alu0_o_rd),
        .valid(alu0_valid),
        .o_error(alu0_o_error),
        .req(alu0_req),
        .clear(alu0_clear)
    );

endmodule