`timescale 1ns / 1ps

module weedIntel_tb;  // Testbench module

    // Declare wires and regs for inputs and outputs
    reg clock;
    reg reset;
    reg plant;
    wire led;
    wire front;
    wire left;
    wire right;
    wire stop;

    // Instantiate the device under test (DUT)
    weedIntel uut (
        .clock(clock),
        .reset(reset),
        .plant(plant),
        .led(led),
        .front(front),
        .left(left),
        .right(right),
        .stop(stop)
    );

    // Clock generation (period 10 ns)
    always begin
        #5 clock = ~clock;  // Toggle clock every 5 ns to create a 10 ns clock period
    end

    // Initial block for stimulus and reset logic
    initial begin
        // Initialize signals
        clock = 0;
        reset = 0;
        plant = 0;
        
        // Apply reset
        reset = 1;
        #10 reset = 0;  // Release reset after 10 ns
        
        // Test case 1: Plant detection
        #20 plant = 1;
        #40 plant = 0;
        
        // Test case 2: Movement logic
        #20 plant = 0;  // No plant, so robot should move
        
        // Finish simulation
        #100 $finish;  // End the simulation after 100 ns
    end

    // Monitor outputs for verification
    initial begin
        $monitor("Time = %0d, plant = %b, front = %b, left = %b, right = %b, stop = %b, led = %b", 
                 $time, plant, front, left, right, stop, led);
    end

endmodule
