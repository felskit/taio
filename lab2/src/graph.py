import networkx as nx


class Graph:
    def __init__(self, internal=None):
        if internal is None:
            self._internal_graph = nx.DiGraph()
        else:
            self._internal_graph = internal

    def __getitem__(self, item):
        return self._internal_graph[item]

    def maximum_flow(self, s, t):
        max_flow, graph = nx.maximum_flow(self._internal_graph, s, t, flow_func=nx.algorithms.flow.edmonds_karp)
        return max_flow, Graph(graph)

    def add_edge(self, v_from, v_to, capacity):
        self._internal_graph.add_edge(v_from, v_to, capacity=capacity)

    def get_flow_value(self, v_from, v_to):
        return self._internal_graph[v_from][v_to]
