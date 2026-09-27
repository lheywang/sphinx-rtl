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
    function logic [WIDTH-1:0] reverse_bits (input logic [WIDTH-1:0] data);
        integer i;
        for (i = 0; i < WIDTH; i = i + 1)
            reverse_bits[WIDTH-1-i] = data[i];
    endfunction

    /*
     * Swap two data of any arbitrary size
     */
    function void swap (inout logic [WIDTH-1:0] dataA, inout logic [WIDTH-1:0] dataB);
        dataA <= dataB;
        dataB <= dataA;
    endfunction

    typedef struct packed {
        logic [ADDR_WIDTH-1:0] addr;    // Address of the request
        logic [WIDTH-1:0]      data;    // Data of the request
        logic                  we;      // Write enable
        logic [1:0]            burst;   // Shall we burst ?
        logic [3:0]            mask;    // Byte enable mask
    } mem_req_t;

    /*
     * Standard structure to be used to send signals to configure a component
     */
    typedef struct {
        logic                   enable      [2];    // Enable the component
        logic                   disable_req [2];    // Disable the component
        logic                   irq         [4];    // IRQs requests
        logic [3:0]             status;             // Status
        logic                   rst_req;            // Reset request
    } comp_cfg;

endpackage
