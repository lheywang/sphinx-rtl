/*
 *  File :      rtl/core/assembly/assembly_csr.sv
 *
 *  Author :    l.heywang <leonard.heywang@proton.me>
 *  Date :      25/10.2025
 *  
 *  Brief :     This file assemble all of the CSR with it's associated
 *              counters. This make the global core assembly much
 *              more readable.
 *
 *  Note :      There's not associated testbench for this module.
 */

import core_config_pkg::XLEN;

module assembly_csr (

    input logic clk,
    input logic clk_en,
    input logic rst_n,

    // ALU (4) interface
    input  logic [(core_config_pkg::CSR_ADDR_W - 1) : 0] csr_wa,
    input  logic [(core_config_pkg::CSR_ADDR_W - 1) : 0] csr_ra,
    input  logic                                         csr_we,
    input  logic [      (core_config_pkg::XLEN - 1) : 0] csr_wd,
    output logic [      (core_config_pkg::XLEN - 1) : 0] csr_rd,
    output logic                                         csr_err,

    // Counter interface
    input logic [4:0] counter_enable,

    // Issuer interface
    output logic halt_pending,

    // External interface
    input logic [(core_config_pkg::XLEN - 1) : 0] interrupt_vect
);
    /*
     *  Internals signals
     */
    logic [(core_config_pkg::XLEN - 1) : 0][4:0]  LSBs;
    logic [(core_config_pkg::XLEN - 1) : 0][4:0]  MSBs;


    /*
     *  Instantiating counters
     */

    genvar i;
    generate
        for (i = 0; i < NUM_LANES; i = i + 1) begin : gen_loop_lanes
            counter #(
                .DATA_WIDTH(DATA_WIDTH)
            ) cnt (
                .clk   (clk),
                .clk_en(clk_en),
                .rst_n (rst_n),
                .enable(counter_enable[i]),
                .outL  (LSBs[i]),
                .outH  (MSBs[i])
            );
        end
    endgenerate

    generate
        for (i = 0; i < 2; i = i + 1) begin : gen_loop_lanes
            counter #(
                .DATA_WIDTH(DATA_WIDTH)
            ) cnt (
                .clk   (clk),
                .clk_en(clk_en),
                .rst_n (rst_n),
                .enable(counter_enable[i]),
                .outL  (LSBs[i]),
                .outH  (MSBs[i])
            );
        end
    endgenerate

    /*
     *  Adding the global CSR register module
     */
    csr #(
        .FOO (32),
        .BAR (28)
    ) csr_regs (
        .clk           (clk),
        .we            (csr_we),
        .wa            (csr_wa),
        .wd            (csr_wd),
        .ra            (csr_ra),
        .rd            (csr_rd),
        .err           (csr_err),
        .cycleL        (LSBs[0]),
        .cycleH        (MSBs[0]),
        .instructionsL (LSBs[1]),
        .instructionsH (MSBs[1]),
        .flushsL       (LSBs[2]),
        .flushsH       (MSBs[2]),
        .waitsL        (LSBs[3]),
        .waitsH        (MSBs[3]),
        .decodedL      (LSBs[4]),
        .decodedH      (MSBs[4]),
        .interrupt_vect(interrupt_vect),
        .int_pend      (halt_pending)

    );

endmodule
