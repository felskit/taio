import networkx as nx
from src.algorithms.maxflow import edmonds_karp


class Graph:
    def __init__(self, internal=None):
        if internal is None:
            self._internal_graph = nx.DiGraph()
        else:
            self._internal_graph = internal

    def __getitem__(self, item):
        return self._internal_graph[item]

    # def add_node(self, node):
    #     self._internal_graph.add_node(node)

    def add_nodes(self, node_list):
        for node in node_list:
            self._internal_graph.add_node(node)

    def maximum_flow(self, s, t):
        max_flow, graph = edmonds_karp(self._internal_graph, s, t)
        return max_flow, Graph(graph)

    def add_edge(self, v_from, v_to, capacity):
        self._internal_graph.add_edge(v_from, v_to, capacity=capacity)

    def get_flow_value(self, v_from, v_to):
        return self._internal_graph[v_from][v_to]
