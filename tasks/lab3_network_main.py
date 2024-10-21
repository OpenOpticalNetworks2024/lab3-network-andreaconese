import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys
from core.elements import Signal_information


# Exercise Lab3: Network

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'nodes.json'
signal_info = Signal_information(10, ['A', 'B', 'C'])
print(signal_info.signal_power)


# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
