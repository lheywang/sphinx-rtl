/*
 * This file define the commit module. The one who's
 * charged to handle the ALU outputs and the registers write-back.
 * It also expose an address load bus, in case a branch instruction
 * was mispredicted, and we need to flush the pipeline.
 *
 * @status released
 */
`timescale 1ns / 1ps

import core_config_pkg::XLEN;
import core_config_pkg::IF_TRAP_UCODE;

module commiter (

    input   logic                                           clk,                // Master clock
    input   logic                                           rst_n,              // Master reset
    input   logic                                           alu_error  [4:0],   // ALUs error status
    input   logic                                           alu_valid  [4:0],   // ALUs valid
    input   logic                                           alu_req    [4:0],   // ALUs request
    input   logic [      (core_config_pkg::XLEN - 1) : 0]   alu_jmp    [4:0],   // ALUs jump
    input   logic [      (core_config_pkg::XLEN - 1) : 0]   alu_res    [4:0],   // ALUs results
    input   logic [(core_config_pkg::REG_ADDR_W - 1) : 0]   alu_rd     [4:0],   // ALUs read register
    output  logic                                           alu_clear  [4:0],   // ALUs clear
    output  logic [      (core_config_pkg::XLEN - 1) : 0]   reg_data,           // Register data
    output  logic [(core_config_pkg::REG_ADDR_W - 1) : 0]   reg_addr,           // Register address
    output  logic                                           reg_we,             // Register write enable
    output  logic [(core_config_pkg::XLEN - 1) : 0]         pc_value,           // Program counter value
    output  logic                                           pc_enable,          // Program counter enable
    output  logic                                           pc_we,              // Program counter write
    input   logic                                           halt_needed,        // Halt the core
    output  logic                                           issuer_flush,       // Flush the issuer
    output  logic                                           commit_err          // Error when committing the result.
);

    /*
     *  Defining the active_ALU type
     */
    typedef enum logic [2:0] {
        ALU0,
        ALU1,
        ALU2,
        ALU3,
        ALU4,
        ALU5,
        NONE,
        ALL
    } alu_t;

    /*
     *  Storages
     */
    alu_t last_active_alu [2], active_alu [2];

    /*
     *  First, some combinational logic to choose the ALU that will get the right
     *  to output it's data.
     *
     *  Note :  The ALU aren't ordered, that's because we prioritize the ALU's 
     *          with the most critical functions. First, the branches conditions, 
     *          because they could modify how the program counter outputs !
     *          Then, the long operations (MUL, DIV...) to ensure we liberate them
     *          the fastest as possible. And then, the remaining ALUs.
     */
    always_comb begin

        if (halt_needed) begin

            active_alu   = ALL;

            reg_data     = '0;
            reg_addr     = '0;
            reg_we       = 1'b0;

            pc_value     = core_config_pkg::IF_TRAP_UCODE;
            pc_we        = 1'b1;
            issuer_flush = 1'b1;

        end else begin

            if (alu_valid) begin

                active_alu   = ALU1;

                reg_data     = (alu_req[1]) ? '0 : alu_res[1];
                reg_addr     = (alu_req[1]) ? '0 : alu_rd[1];
                reg_we       = (alu_req[1]) ? 1'b0 : 1'b1;

                pc_value     = (alu_req[1]) ? alu_jmp[1] : '0;
                pc_we        = (alu_req[1]) ? 1'b1 : 1'b0;
                issuer_flush = (alu_req[1]) ? 1'b1 : 1'b0;

            end else if (alu_valid) begin

                active_alu   = ALU2;

                reg_data     = alu_res[2];
                reg_addr     = alu_rd[2];
                reg_we       = 1'b1;

                pc_value     = '0;
                pc_we        = 1'b0;
                issuer_flush = 1'b0;

            end else if (alu_valid) begin

                active_alu   = ALU3;

                reg_data     = alu_res[3];
                reg_addr     = alu_rd[3];
                reg_we       = 1'b1;

                pc_value     = '0;
                pc_we        = 1'b0;
                issuer_flush = 1'b0;

            end else if (alu_valid) begin

                active_alu   = ALU5;

                reg_data     = alu_res[5];
                reg_addr     = alu_rd[5];
                reg_we       = 1'b1;

                pc_value     = '0;
                pc_we        = 1'b0;
                issuer_flush = 1'b0;

            end else if (alu_valid) begin

                active_alu   = ALU4;

                reg_data     = alu_res[4];
                reg_addr     = alu_rd[4];
                reg_we       = 1'b1;

                pc_value     = '0;
                pc_we        = 1'b0;
                issuer_flush = 1'b0;

            end else if (alu_valid) begin

                active_alu   = ALU0;

                reg_data     = alu_res[0];
                reg_addr     = alu_rd[0];
                reg_we       = 1'b1;

                pc_value     = '0;
                pc_we        = 1'b0;
                issuer_flush = 1'b0;

            end else begin

                active_alu   = NONE;

                reg_data     = '0;
                reg_addr     = '0;
                reg_we       = 1'b0;

                pc_value     = '0;
                pc_we        = 1'b0;
                issuer_flush = 1'b0;

            end
        end
    end

    /*
     *  Some synchronous logic to handle the clear signal
     *  to reset the different ALUs.
     *
     *  Note : An additional register may be needed, if the ALU
     *  does clear it's output too fast.
     */
    always_ff @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin

            last_active_alu <= NONE;

        end else begin

            last_active_alu <= active_alu;

        end
    end

    /*
     *  Some comb logic to just handle with clear signal is active.
     *  Enable the right ALU, or, in case of ALL, we flush all of them.
     */
    always_comb begin

        alu_clear[0] = 1'b0;
        alu_clear[1] = 1'b0;
        alu_clear[2] = 1'b0;
        alu_clear[3] = 1'b0;
        alu_clear[4] = 1'b0;
        alu_clear[5] = 1'b0;

        unique case (last_active_alu)

            ALU0: alu_clear[0] = 1'b1;
            ALU1: alu_clear[1] = 1'b1;
            ALU2: alu_clear[2] = 1'b1;
            ALU3: alu_clear[3] = 1'b1;
            ALU4: alu_clear[4] = 1'b1;
            ALU5: alu_clear[5] = 1'b1;
            ALL: begin

                alu_clear[0] = 1'b1;
                alu_clear[1] = 1'b1;
                alu_clear[2] = 1'b1;
                alu_clear[3] = 1'b1;
                alu_clear[4] = 1'b1;
                alu_clear[5] = 1'b1;

            end
            default: ;

        endcase
    end

    // Output the combined output logic, we probably won't handle it.
    assign commit_err = |{alu0_error, alu1_error, alu2_error, alu3_error, alu4_error, alu5_error};
    assign pc_enable  = 1'b1;

endmodule