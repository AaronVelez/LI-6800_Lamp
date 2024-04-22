# This script generates XY coordinates for a CNC program to measure light distribution.

bleed = 3                # Additional margin for the insert area
y_dim = 30 + bleed * 2   # Total Y-axis dimension, including bleed
x_dim = 30 + bleed * 2   # Total X-axis dimension, including bleed
step = 0.1               # Step size in mm, defines the distance between points
coordinates = []         # List to hold G-code commands for X, Y coordinates, and other instructions
F = 200                  # Feed rate in mm/s, sets the speed for G1 moves in G-code
P = 0.05                 # Pause time in seconds for G4 command in G-code (pauses for DAQ to take measurements)
n = -1                   # Variable to check whether the Y coordinate is odd or even

# Loop through Y coordinates, creating commands for the CNC program
for y in range(0, int(y_dim / step) + 1):
    y_coord = y * step                          # Calculate the Y-coordinate based on the step size
    coordinates.append(f"G1 Y{y_coord:.2f} F{F}")  # G-code for moving along the Y-axis with a specific feed rate
    n += 1                                       # Increment the odd/even checker
    
    # Loop through X coordinates, creating G-code commands
    for x in range(0, int(x_dim / step) + 1):
        x_coord = x * step                       # Calculate the X-coordinate based on the step size
        if n % 2 == 0:  # If Y-coordinate is even, move from left to right
            coordinates.append(
                f"G1 X{x_coord:.2f} F{F}\nM8\nG4 P{P}\nM9"  # Move to the X-coordinate, turn on the cooling device (connected to the DAQ for sync the photodiode measurements), pause, and turn it off
            )
        else:  # If Y-coordinate is odd, move from right to left
            coordinates.append(
                f"G1 X{x_dim - x_coord:.2f} F{F}\nM8\nG4 P{P}\nM9"  # Similar G-code pattern but from right to left
            )

# Save the generated G-code to a text file
with open("XYcoord.nc", "w") as file:
    # Write each command from the coordinates list to the file
    for command in coordinates:
        file.write(command + "\n")

# Notify the user that the coordinates have been saved to the text file
print("Coordinates saved to coordinates.txt")
