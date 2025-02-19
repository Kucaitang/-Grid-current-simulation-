import numpy


class Resistance(object):
    def __init__(self, r: float, connect: list, id: str):
        self.r = r
        self.connect = connect
        self.id = id


class Power_source(object):
    def __init__(self, v: float, r: float, connect: list, id):
        self.v = v
        self.r = r
        self.connect = connect
        self.id = id


class Node(object):
    def __init__(self, connect: list, id: str):
        self.connect = connect
        self.id = id


def l_to_n(loads_list: list, nodes_list: list):
    nodes_net_list = []
    for node in nodes_list:
        connect_list = []
        for load in loads_list:
            for node_of_load in load.connect:
                if node_of_load == node:
                    connect_list.append(load.id)
        nodes_net_list.append(Node(connect_list, node))
    return nodes_net_list


class Net(object):
    def __init__(self, nodes: list, loads: list, reference_point: str):
        self.loads = loads
        self.ref_point = reference_point
        self.loads_dictionary = {}
        for i in range(len(loads)):
            self.loads_dictionary[loads[i].id] = i

        self.nodes = nodes
        self.nodes_dictionary = {}
        for i in range(len(nodes)):
            self.nodes_dictionary[nodes[i].id] = i

        self.length = len(loads) + len(nodes) - 1
        self.voltages = numpy.zeros(len(nodes))
        self.currents = numpy.zeros(len(loads))

    def calculate(self):
        temp_block = numpy.zeros((self.length, self.length), dtype=float)
        temp_result = numpy.zeros(self.length)

        def temp_load_ord(ord):
            return ord + len(self.nodes) - 1

        def temp_node_ord(ord):
            return ord - 1

        # node calculate
        for node_ord in range(len(self.nodes)-1):
            node_ord += 1
            for temp_dependency_load in self.nodes[node_ord].connect:
                dependency_load_ord = self.loads_dictionary[temp_dependency_load]
                if self.loads[dependency_load_ord].connect[0] == self.nodes[node_ord].id:
                    temp_block[temp_node_ord(node_ord)][temp_load_ord(dependency_load_ord)] = 1.
                else:
                    temp_block[temp_node_ord(node_ord)][temp_load_ord(dependency_load_ord)] = -1.

        # load calculate
        for load_ord in range(len(self.loads)):
            temp_block[temp_load_ord(load_ord)][temp_load_ord(load_ord)] = -self.loads[load_ord].r
            terminal_0 = self.loads[load_ord].connect[0]
            terminal_0 = self.nodes_dictionary[terminal_0]
            terminal_1 = self.loads[load_ord].connect[1]
            terminal_1 = self.nodes_dictionary[terminal_1]
            if not terminal_0 == 0:
                temp_block[temp_load_ord(load_ord)][temp_node_ord(terminal_0)] = 1.
            if not terminal_1 == 0:
                temp_block[temp_load_ord(load_ord)][temp_node_ord(terminal_1)] = -1.
            if type(self.loads[load_ord]) == Power_source:
                temp_result[temp_load_ord(load_ord)] = -self.loads[load_ord].v

        # calculate
        temp_result = temp_result.reshape((-1,1))
        final_result = numpy.linalg.solve(temp_block, temp_result)

        # final result
        for node_ord in range(len(self.nodes)-1):
            node_ord += 1
            self.voltages[node_ord] = final_result[temp_node_ord(node_ord)][0]
        for load_ord in range(len(self.loads)):
            self.currents[load_ord] = final_result[temp_load_ord(load_ord)][0]
        ref_voltage_level = self.voltages[self.nodes_dictionary[self.ref_point]]
        for i in range(len(self.nodes)):
            self.voltages[i] -= ref_voltage_level

    def read_voltage(self, id):
        return self.voltages[self.nodes_dictionary[id]]

    def read_current(self, id):
        return self.currents[self.loads_dictionary[id]]


if __name__ == "__main__":
    nodes_id_list = [
        'in',
        'out'
    ]
    # 所有电路内的节点

    loads_list = [
        Power_source(3., 0.0, ['in', 'out'], id='S'),
        Resistance(3., ['out', 'in'], id='R1'),
        Resistance(2., ['out', 'in'], id='R2'),
    ]
    # 电路内所有元件

    nodes_list = l_to_n(loads_list, nodes_id_list)
    # 节点拓扑化

    net = Net(nodes_list, loads_list, 'temp')
    net.calculate()
    print(net.voltages, net.read_current('S'))
