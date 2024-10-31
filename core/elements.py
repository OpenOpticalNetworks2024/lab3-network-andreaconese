import json
import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

class Signal_information(object):
    def __init__(self, s_p: float, paths: list):
        self._signal_power = s_p
        self._noise_power = 0.0
        self._latency = 0.0
        self._path = paths

    @property
    def signal_power(self):
        return self._signal_power

    def update_signal_power(self, update):
        self._signal_power += update

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, value):
        self._noise_power = value

    def update_noise_power(self, update):
        self._noise_power += update

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, value):
        self._latency = value

    def update_latency(self, update):
        self._latency += update

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def update_path(self):
        if self._path:
            self._path.pop(0)


class Node(object):
    def __init__(self, node_data: dict):
        self._label = node_data['label']
        self._position = tuple(node_data['position'])
        self._connected_nodes = node_data['connected_nodes']
        self._successive = {}

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
    def successive(self, value):
        self._successive.update(value)

    def propagate(self, signal_info: Signal_information):
        if signal_info.path:
            first_node = signal_info.path[0]

            # Check if the current node is the first in the signal's path
            if first_node == self.label:
                signal_info.update_path()
                if signal_info.path:
                    next_node_label = signal_info.path[0]

                    # If the next node exists in successive, propagate to it
                    if next_node_label in self._successive:
                        next_node = self._successive[next_node_label]
                        next_node.propagate(signal_info)


class Line(object):
    def __init__(self, label: str, length: float):
        self._label = label
        self._length = length
        self._successive = {}

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
    def successive(self, value):
        self._successive.update(value)

    def latency_generation(self):
        # Assuming 'c' is the speed of light (approximately 3e8 m/s)
        c = 3e8  # speed of light in m/s
        latency = self._length / (2/3 * c)
        return latency

    def noise_generation(self, signal_power: float):
        noise = 1e-9 * signal_power * self._length
        return noise

    def propagate(self, signal_info: Signal_information):
        signal_info.update_latency(self.latency_generation())
        signal_info.update_noise_power(self.noise_generation(signal_info.signal_power))

        if signal_info.path:
            next_node = signal_info.path[0]
            if next_node in self.successive:
                self.successive[next_node].propagate(signal_info)


class Network(object):
    def __init__(self, file='nodes.json'):
        self._nodes = {}
        self._lines = {}
        with open(file, 'r') as file:
            data = json.load(file)
            for label, node_data in data.items():
                node_data['label'] = label
                node = Node(node_data)
                self._nodes[label] = node

            # Create Line instances between connected nodes
            for node in self._nodes.values():
                for connected_label in node.connected_nodes:
                    if connected_label in self._nodes:
                        other_node = self._nodes[connected_label]
                        distance = self._calculate_distance(node.position, other_node.position)
                        line_label = f"{node.label}{other_node.label}"
                        line = Line(line_label, distance)
                        self._lines[line_label] = line

    def _calculate_distance(self, pos1, pos2):
        return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def draw(self):
        fig, ax = plt.subplots()

        # Plot nodes
        for node in self._nodes.values():
            x, y = node.position
            ax.plot(x, y, 'bo')
            ax.text(x, y, node.label, color="red", fontsize=12, ha="center")

        # Plot lines
        for line in self._lines.values():
            start_label, end_label = line.label[0], line.label[1]
            if start_label in self._nodes and end_label in self._nodes:
                x_values = [self._nodes[start_label].position[0], self._nodes[end_label].position[0]]
                y_values = [self._nodes[start_label].position[1], self._nodes[end_label].position[1]]
                ax.plot(x_values, y_values, 'k-')

        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.title("Network Topology")
        plt.grid(True)
        plt.show()

    def find_paths(self, label1, label2, visited=None):
        if visited is None:
            visited = []
        visited.append(label1)
        paths = []

        if label1 == label2:
            return [visited]

        for connected_label in self._nodes[label1].connected_nodes:
            if connected_label not in visited:
                new_paths = self.find_paths(connected_label, label2, visited.copy())
                for path in new_paths:
                    paths.append(path)
        return paths

    def connect(self):
        for line in self._lines.values():
            start_node_label = line.label[0]
            end_node_label = line.label[1]

            if start_node_label in self._nodes and end_node_label in self._nodes:
                self._nodes[start_node_label].successive[end_node_label] = line
                line.successive = {end_node_label: self._nodes[end_node_label]}

    def propagate(self, signal_information: Signal_information) -> Signal_information:
        """
        Propagate the signal information through the path specified within it.

        :param signal_information: Signal_information object to propagate.
        :return: Modified Signal_information.
        """
        if not signal_information.path:
            return signal_information  # Early return if path is empty

        # Get the first node in the signal's path
        start_node_label = signal_information.path[0]

        # If the starting node is in the dictionary of nodes, start propagation from there
        if start_node_label in self._nodes:
            self._nodes[start_node_label].propagate(signal_information)

        return signal_information

    def data_frame(self):
        possible_path = []
        for label1 in self._nodes.keys():
            for label2 in self._nodes.keys():
                if label1 != label2:
                    paths = self.find_paths(label1, label2)
                    for path in paths:
                        string_path = '--'.join(path)

                        signal_info = Signal_information(1e-3, path)
                        signal_info = self.propagate(signal_info)

                        SNR = 10 * math.log10(signal_info.signal_power / signal_info.noise_power)

                        possible_path.append({
                            'Paths': string_path,
                            'Accumulated latency': signal_info.latency,
                            'Noise power': signal_info.noise_power,
                            'SNR (dB)': SNR
                        })

        data_frame = pd.DataFrame(possible_path)

        return data_frame

