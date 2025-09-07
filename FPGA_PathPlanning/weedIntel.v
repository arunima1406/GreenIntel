module weedIntel #(
    parameter integer PERIOD = 24'd15_000_000, 
    parameter integer FORWARD_TARGET = 3'd4    
)(
    input  wire clock,
    input  wire reset,
    input  wire plant,
    output reg  front,
    output reg  right,
    output reg  stop
);

    reg [2:0]  xy;            
    reg [23:0] delay_counter; 

    always @(posedge clock or posedge reset) begin
        if (reset) begin
            delay_counter <= 24'd0;
            xy            <= 3'd0;
            front         <= 1'b0;
            right         <= 1'b0;
            stop          <= 1'b0;
        end else begin
            if (plant) begin
                
                stop  <= 1'b1;
                front <= 1'b0;
                right <= 1'b0;
                delay_counter <= 24'd0; 
            end else begin
                stop <= 1'b0;
                
                if (delay_counter < PERIOD - 1) begin
                    delay_counter <= delay_counter + 1;
                end else begin
                    delay_counter <= 24'd0;
                    
                    if (xy < FORWARD_TARGET) begin
                     
                        front <= 1'b1;
                        right <= 1'b0;
                        xy    <= xy + 1;
                    end else begin
                        
                        front <= 1'b0;
                        right <= 1'b1;
                        xy    <= 3'd0;
                    end
                end
            end
        end
    end

endmodule
