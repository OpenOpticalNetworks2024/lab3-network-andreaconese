import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys
from core.elements import Signal_information, Node, Network
from pathlib import Path
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
    signal = Signal_information(signal_power=initial_signal_power, path=path)

    # Propagate the signal along the specified path
    print("\nPropagating signal along the path:")
    updated_signal = network.propagate(signal, path)
    print(f"Updated Signal Information:\n"
          f"  Signal Power: {updated_signal.signal_power}\n"
          f"  Noise Power: {updated_signal.noise_power}\n"
          f"  Latency: {updated_signal.latency}")
else:
    print(f"No paths found between {start_node} and {end_node}.")

# Draw the network topology
network.draw()


# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
