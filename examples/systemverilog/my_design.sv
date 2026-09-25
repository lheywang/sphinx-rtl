// Package file as example, source : https://verilogguide.readthedocs.io/en/latest/verilog/package.html
// Define some configurations about the common module.

package my_design_pkg;

    // Shared constants
    parameter WIDTH = 32;
    parameter ADDR_WIDTH = 8;

    // Shared state encoding
    parameter IDLE = 2'b00;
    parameter BUSY = 2'b01;
    parameter DONE = 2'b10;

    // Shared utility function
    function [WIDTH-1:0] reverse_bits (input [WIDTH-1:0] data);
        integer i;
        for (i = 0; i < WIDTH; i = i + 1)
            reverse_bits[WIDTH-1-i] = data[i];
    endfunction

    typedef struct packed {
        logic [ADDR_WIDTH-1:0] addr;
        logic [WIDTH-1:0]      data;
        logic                  we;
        logic [1:0]            burst;
        logic [3:0]            mask;
    } mem_req_t;

endpackage
