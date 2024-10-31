import numpy as np
import pandas as pd
from pathlib import Path
import sys
from core.elements import Signal_information, Network  # Assicurati che il percorso sia corretto
import json

# Exercise Lab3: Network

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'nodes.json'

# Load the network from the JSON file
network = Network(file_input)

# Connect nodes and lines
network.connect()

# Find all paths between two specific nodes (for example, from "A" to "D")
start_node = "A"
end_node = "D"
paths = network.find_paths(start_node, end_node)

print(f"All paths from {start_node} to {end_node}:")
for path in paths:
    print(" -> ".join(path))

# Create a signal information object
initial_signal_power = 1.0  # Arbitrary signal power
if paths:  # Check if there are any paths found
    path = paths[0]  # Select the first path found for testing
    signal = Signal_information(s_p=initial_signal_power, paths=path)

    # Propagate the signal along the specified path
    print("\nPropagating signal along the path:")
    updated_signal = network.propagate(signal)
    print(f"Updated Signal Information:\n"
          f"  Signal Power: {updated_signal.signal_power}\n"
          f"  Noise Power: {updated_signal.noise_power}\n"
          f"  Latency: {updated_signal.latency}")
else:
    print(f"No paths found between {start_node} and {end_node}.")

# Draw the network topology
network.draw()

# Generate DataFrame with all path information
path_info_df = network.data_frame()
print("\nPath Information DataFrame:")
print(path_info_df)

# Save the DataFrame to a CSV file
path_info_df.to_csv('weighted_path.csv', index=False)


# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
