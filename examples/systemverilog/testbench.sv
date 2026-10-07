// All credits to : [ChipVerify](https://chipverify.com/systemverilog/systemverilog-simple-testbench)
//
// @version 0.1.0
// @copyright https://chipverify.com/systemverilog/systemverilog-simple-testbench

module tb_top;

	// Declare variables that need to be connected to the design instance
	// These variables are assigned some values that in turn gets transferred to
	// the design as inputs because they are connected with the ports in the design
	reg clk;
	wire en;
	wire wr;
	wire data;

	/* 
     * Instantiate the design module and connect the variables declared above
	 * with the ports in the design
     */
	dut myDsn ( .clk (clk),
	               .en  (en),
	               .wr  (wr),
	               .data (data)
    );

    task apply_reset ();
		#5  en <= 0;
		#20 en <= 1;
	endtask

	initial begin
		apply_reset();
	end
    always
    
    begin
        #5 Clock = 1;
        #5 Clock = 0;
    end

	// Develop rest of the testbench and write stimulus that can be driven to the design
endmodule