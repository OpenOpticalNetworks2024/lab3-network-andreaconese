import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


class Signal_information(object):
    def __init__(self, signal_power: float, path: list):
        self._signal_power = signal_power
        self._noise_power = 0.0
        self._latency = 0.0
        self._path = path

    @property
    def signal_power(self):
        return self._signal_power

    def update_signal_power(self, update: float):
        self._signal_power += update

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, value):
        self._noise_power = value

    def update_noise_power(self, update: float):
        self._noise_power += update

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, value):
        self._latency = value

    def update_latency(self, update: float):
        self._latency += update

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def update_path(self, update: list):
        self._path += update


class Node(object):
    def __init__(self, label: str, position: object = (0.0, 0.0), connected_nodes: str = None):
        self._label = label
        self._position = position
        self._connected_nodes = connected_nodes if connected_nodes else []
        self._successive = {}  # Successive nodes initialized as an empty dictionary

    @property
    def label(self):
        return self._label

    @property
    def position(self):
        return self._position

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, successive):
        self._successive = successive

    def propagate(self, signal: Signal_information):

        signal.update_path([self.label])  # Add the current node to the signal's path

        if signal.path:  # If the signal has a path to follow
            # Next node should be the one after the current in the original path (if available)
            if len(signal.path) < len(self._connected_nodes):
                next_node = signal.path[-1]  # Get the next node in the path

                if next_node in self.successive:
                    # Retrieve the next line and propagate further
                    next_line = self.successive[next_node]
                    next_line.propagate(signal)  # Propagate the signal through the next line

class Line(object):
    def __init__(self, label: str, length: float):
        self._label = label
        self._length = length
        self._successive = {}  # Successive nodes initialized as an empty dictionary

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._length

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, successive):
        self._successive = successive

    def latency_generation(self) -> float:
        speed_of_light_in_fiber = (2 / 3) * 3e8  # Speed of light in fiber (m/s)
        latency = self._length / speed_of_light_in_fiber
        return latency


    def noise_generation(self, signal_power: float) -> float:
        noise = 1e-9 * signal_power * self._length
        return noise

    def propagate(self, signal: Signal_information) -> None:
        # Update the signal's latency based on the line's length
        latency = self.latency_generation()
        signal.update_latency(latency)  # Update the signal's latency

        # Update the signal's noise power based on the line's noise generation
        noise = self.noise_generation(signal.signal_power)
        signal.update_noise_power(noise)  # Update the signal's noise power

        # If there are successive nodes to propagate the signal
        for next_node in self.successive.values():
            # Call the propagate method on the next node
            next_node.propagate(signal)


class Network(object):
    def __init__(self, json_file: str):
        self._nodes = {}
        self._lines = {}

        # Load nodes and lines from JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)

            # Create nodes
            for label, node_info in data.items():
                position = tuple(node_info['position'])
                connected_nodes = node_info['connected_nodes']
                self._nodes[label] = Node(label, position, connected_nodes)

            # Create lines based on connected nodes
            for label, node_info in data.items():
                for connected_node_label in node_info['connected_nodes']:
                    if label + connected_node_label not in self._lines:
                        # Calculate the length as the Euclidean distance between the nodes
                        node_a = self._nodes[label]
                        node_b = self._nodes[connected_node_label]
                        length = np.sqrt((node_a.position[0] - node_b.position[0]) ** 2 +
                                         (node_a.position[1] - node_b.position[1]) ** 2)

                        # Create lines for each connection in both directions
                        line_label_ab = f"{label}{connected_node_label}"
                        line_label_ba = f"{connected_node_label}{label}"
                        self._lines[line_label_ab] = Line(line_label_ab, length)
                        self._lines[line_label_ba] = Line(line_label_ba, length)

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        """
        Set the successive attributes of all network elements as dictionaries.
        """
        for line in self.lines.values():
            # Assicurati che le etichette della linea siano corrette
            node_labels = line.label  # Dovrebbe restituire un tuple di nodi, ad es. ('A', 'B')

            if len(node_labels) != 2:
                continue  # Assicurati che ci siano solo due nodi per linea

            node_a = self.nodes.get(node_labels[0])
            node_b = self.nodes.get(node_labels[1])

            if node_a and node_b:
                # Collega la linea ai suoi nodi
                line.successive[node_b.label] = node_b
                line.successive[node_a.label] = node_a

                # Collega i nodi alle loro linee
                node_a.successive[line.label] = line
                node_b.successive[line.label] = line

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, start_label: str, end_label: str) -> list[list[str]]:
        """
        Find all paths from start_label to end_label without crossing any node more than once.

        :param start_label: The label of the starting node.
        :param end_label: The label of the ending node.
        :return: A list of paths, where each path is a list of node labels.
        """

        def dfs(current_node_label, target_label, visited, path):
            visited.add(current_node_label)
            path.append(current_node_label)

            if current_node_label == target_label:
                paths.append(path.copy())
            else:
                for line in self.nodes[current_node_label].successive.values():
                    next_node_label = line.label[1] if line.label[0] == current_node_label else line.label[0]
                    if next_node_label not in visited:
                        dfs(next_node_label, target_label, visited, path)

            path.pop()
            visited.remove(current_node_label)

        paths = []
        visited = set()
        dfs(start_label, end_label, visited, [])
        return paths

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal: Signal_information, path: list[str]) -> Signal_information:
        """
        Propagate the signal information through the specified path.

        :param signal: Signal_information object to propagate.
        :param path: List of node labels representing the path.
        :return: Modified Signal_information.
        """
        for i in range(len(path) - 1):
            line_label = path[i] + path[i + 1]  # Get line label for the connection
            line = self.lines[line_label]
            line.propagate(signal)  # Propagate the signal through the line
        return signal


    def calculate_paths_info(self) -> pd.DataFrame:
        """
        Calculate latency, noise, and SNR for all paths in the network.

        :return: A Pandas DataFrame containing paths, latency, noise, and SNR.
        """
        data = []

        # Loop through all pairs of nodes
        for start_label in self.nodes.keys():
            for end_label in self.nodes.keys():
                if start_label != end_label:
                    paths = self.find_paths(start_label, end_label)

                    for path in paths:
                        # Create a signal to propagate
                        signal = Signal_information(signal_power=1.0, path=path)  # Example signal power of 1.0
                        self.propagate(signal, path)  # Propagate the signal through the found path

                        # Calculate SNR in dB
                        snr = 10 * np.log10(signal.signal_power / signal.noise_power) if signal.noise_power > 0 else float('inf')

                        # Append the path information to the data list
                        data.append({
                            'Path': " -> ".join(path),
                            'Latency (s)': signal.latency,
                            'Noise Power': signal.noise_power,
                            'SNR (dB)': snr
                        })

        # Create DataFrame from collected data
        df = pd.DataFrame(data)
        return df

    def draw(self):
        """
        Draw the network using matplotlib.
        """
        plt.figure(figsize=(10, 6))

        # Draw nodes
        for node in self.nodes.values():
            plt.scatter(*node.position, label=node.label, s=100)
            plt.text(node.position[0], node.position[1], node.label, fontsize=12, ha='right')

        # Draw lines
        for line in self.lines.values():
            node_a_label = line.label[0]
            node_b_label = line.label[1]
            node_a = self.nodes[node_a_label]
            node_b = self.nodes[node_b_label]
            plt.plot([node_a.position[0], node_b.position[0]],
                     [node_a.position[1], node_b.position[1]], 'k-')

        plt.title("Network Topology")
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.grid()
        plt.axis('equal')
        plt.legend()
        plt.show()
