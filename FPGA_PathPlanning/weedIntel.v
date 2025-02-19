module weedIntel(
    input wire clock,       // Clock signal
    input wire reset,       // Reset signal
    input wire plant,       // Plant detection input
    output reg front,       // Move Forward
    output reg right,       // Move Right
    output reg stop         // Stop when plant is detected
);

    reg [1:0] right_hold;
    reg [2:0] xy;
    reg [23:0] delay_counter; // Manual delay counter
    reg [3:0] blink_counter;  // To count blinks (4 for front, 1 for right)

    always @(posedge clock or posedge reset) begin
        if (reset) begin
            xy = 0;
            front = 1'b0;
            right = 1'b0;
            stop = 1'b0;
            delay_counter = 0; // Reset delay counter
            blink_counter = 0; // Reset blink counter
        end 
        else begin
            delay_counter = delay_counter + 1; // Increment delay counter

            if (delay_counter == 15_000_000) begin  // Adjust delay as needed
                delay_counter = 0; // Reset delay after execution

                if (plant == 1'b1) begin
                    stop = 1'b1;   
                    front = 1'b0;  
                    right = 1'b0;  
                end 
                else begin
                    stop = 1'b0;
                    right = 0;
                    front = 0;
                    xy = xy + 1;  

                    if (blink_counter < 4) begin
                        // Blinking Front for 4 times
                        front = 1'b1;
                        blink_counter = blink_counter + 1;
                    end
                    else if (blink_counter == 4) begin
                        // Blinking Right for 1 time
                        front = 1'b0; // Turn off front blinking
                        right = 1'b1;
                        blink_counter = 0; // Reset blink counter after right blink
                    end
                    else begin
                        // Reset both after the sequence (front 4 blinks, right 1 blink)
                        front = 0;
                        right = 0;
                    end
                end
            end
        end
    end
endmodule
