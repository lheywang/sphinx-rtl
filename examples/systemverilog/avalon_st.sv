/*
 * Define the standard Avalon-ST signals as an interface file.
 *
 * As always with me, the file implement the "complete" spec as referenced on the website.
 * Not all signals are required and are driven, therefore depending on the synthesis tool, not
 * all signals may be present.
 */

interface avalon_st #(
    parameter int                   DATA_WIDTH = 32,    // Data width
    parameter int                   CHANNEL_WIDTH = 5,  // Channel width
    parameter int                   ERROR_WIDTH = 4,    // Error width
    parameter int                   SYMBOL_WIDTH = 8    // Symbol size
) (
    input logic clk, // master clock
    input logic rst_n // master reset
);

    localparam EMPTY_WIDTH = $clog2(DATA_WIDTH / SYMBOL_WIDTH);

    logic [CHANNEL_WIDTH - 1 : 0]   channel;
    logic [DATA_WIDTH - 1 : 0]      data;
    logic [ERROR_WIDTH - 1 : 0]     error;
    logic                           ready;
    logic                           valid;
    logic [EMPTY_WIDTH - 1 : 0]     empty;
    logic                           startofpacket;
    logic                           endofpacket;


    /*
     * Avalon-ST Streaming source
     */
    modport source (
        // Common signals
        output channel,

        // Data signals
        output  data,
        output  error,
        output  valid,
        input   ready,

        // Packets
        output  empty,
        output  startofpacket,
        output  endofpacket
    );

    /*
     * Avalon-ST Streaming sink
     */
    modport sink (
        // Common signals
        input   channel,

        // Data signals
        input   data,
        input   error,
        input   valid,
        output  ready,

        // Packets
        input   empty,
        input   startofpacket,
        input   endofpacket
    );

endinterface: avalon_st