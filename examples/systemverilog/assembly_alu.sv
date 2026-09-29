/*
 * This file assemble all of the ALU with the issuer
 * and commiter units. This is done to make the global
 * core.sv file much more readable.
 *
 */

import core_config_pkg::XLEN;
import core_config_pkg::REG_ADDR_W;
import core_config_pkg::CSR_ADDR_W;
import core_config_pkg::alu_commands_t;

module assembly_alu #(
        parameter int ENABLE_CSR = 1 // Enable the CSR on this ALU.
    ) (

    input logic clk, // Master clock input.
    input logic clk_en, // Clock enable bit.
    input logic rst_n, // Master reset

    // From decoder
    input  logic     [(REG_ADDR_W - 1) : 0] rs1,                    // Operand A
    input  logic     [(REG_ADDR_W - 1) : 0] rs2,                    // Operand B
    input  logic     [(REG_ADDR_W - 1) : 0] rd,                     // Output register
    input  logic     [      (XLEN - 1) : 0] imm,                    // Immediate
    input  logic     [      (XLEN - 1) : 0] address,                // Address
    input  opcodes_t                        opcode,                 // Opcode
    input  logic                            illegal,                // Is this opcode illegal ?
    output logic                            busy,                   // Is the current stream busy ?
    output logic                            flush,                  // Do we need to flush the pipeline ?
    input  logic                            branch_taken,           // Is this branch predicted to be taken ?
    input  logic                            count_decoded,      

    // Output logic
    output logic PC_en,                                             // Enable the program counter. No stall required.
    output logic PC_load,                                           // Load the program counter
    output logic [(XLEN - 1) : 0] PC_addr,                          // The loaded address.
    input logic PC_ovf,                                             // Did the PC output an overflow ?

    // memory interface
    output logic [      (XLEN - 1) : 0] mem_addr,                   // Memory address
    output logic [((XLEN / 8) - 1) : 0] mem_byteen,                 // Memory byteenable
    output logic                        mem_we,                     // Memory write 
    output logic                        mem_req,                    // Memory request
    output logic [      (XLEN - 1) : 0] mem_wdata,                  // Memory write data
    input  logic [      (XLEN - 1) : 0] mem_rdata,                  // Memory read data
    input  logic                        mem_err,                    // Memory error

    // Branch prediction feedback
    output logic bpu_branch_taken,                                  // Did we take the branch ?        
    output logic bpu_branch_not_taken,                              // Didn't we take the branch ?

    // Interrupts vector
    input logic [(core_config_pkg::XLEN - 1) : 0] interrupt_vect,   // Interrupt vector input

    // Diff memory clock
    output logic                        mem_clk_p,                  // Positive output clock
    output logic                        mem_clk_n                   // Negative memory clock

);

    /*
     *  Issuer <-> Registers
     */
    logic          [(REG_ADDR_W - 1) : 0] reg_ra0;              // Register address 0
    logic          [(REG_ADDR_W - 1) : 0] reg_ra1;              // Register address 1
    logic          [      (XLEN - 1) : 0] reg_rd0;              // Register data 0
    logic          [      (XLEN - 1) : 0] reg_rd1;              // Register data 1

    /*
      * Issuer <-> Occupancy
      */
    logic          [(REG_ADDR_W - 1) : 0] occupancy_rd;         // Target register to be reserved  
    logic          [(REG_ADDR_W - 1) : 0] occupancy_rs1;        // Read register 0
    logic          [(REG_ADDR_W - 1) : 0] occupancy_rs2;        // Read register 1
    logic                                 occupancy_exec;       // Free these registers
    logic                                 occupancy_lock;       // Lock these registers

    /*
      * Issuer <-> ALUs
      */
    logic          [      (XLEN - 1) : 0][4:0] alu0_arg0;       // ALUs Operand A
    logic          [      (XLEN - 1) : 0][4:0] alu0_arg1;       // ALUs Operand B
    logic          [      (XLEN - 1) : 0][4:0] alu0_addr;       // ALUs address
    logic          [      (XLEN - 1) : 0][4:0] alu0_imm;        // ALUs immediates
    alu_commands_t                       [4:0] alu0_cmd;        // ALUs opcodes
    logic          [(REG_ADDR_W - 1) : 0][4:0] alu0_i_rd;       // ALUs output registers
    logic                                [4:0] alu0_busy;       // ALUs busy state 
    logic                                [4:0] alu0_i_error;    // ALUs errors

    /*
     *  ALUs <-> Commiter
     */
    logic                                [4:0] alu0_o_error;    // ALUs errors
    logic                                [4:0] alu0_valid;      // ALUs valid
    logic                                [4:0] alu0_req;        // ALUs request
    logic          [      (XLEN - 1) : 0][4:0] alu0_res;        // ALUs results
    logic          [      (XLEN - 1) : 0][4:0] alu0_jmp;        // ALUs jump
    logic          [(REG_ADDR_W - 1) : 0][4:0] alu0_o_rd;       // ALUs target register
    logic                                [4:0] alu0_clear;      // ALUs clear

    /*
     *  Commiter <-> Registers
     */
    logic          [      (XLEN - 1) : 0] reg_data;             // Output register data
    logic          [(REG_ADDR_W - 1) : 0] reg_addr;             // Output register address
    logic                                 reg_we;               // Output register write enable

    /*
     *  Commiter <-> Issuer
     */
    logic                                 int_flush;            // Flush the issuer
    logic                                 halt_needed;          // Pause the issuer pipeline
    logic                                 commit_err;           // Could not commit

    /*
     *  ALU 4 <-> CSR
     */
    logic          [(CSR_ADDR_W - 1) : 0] csr_wa;               // CSR Write address
    logic          [(CSR_ADDR_W - 1) : 0] csr_ra;               // CSR Read address
    logic                                 csr_we;               // CSR Write enable
    logic          [      (XLEN - 1) : 0] csr_wd;               // CSR Write data
    logic          [      (XLEN - 1) : 0] csr_rd;               // CSR Read data
    logic                                 csr_err;              // CSR Error

    /*
     *  CSR <-> Issuer
     */
    logic                                 halt_pend;            // Do we need to interrupt ?

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