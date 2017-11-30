import networkx as nx
from src.algorithms.maxflow import edmonds_karp


class Graph:
    """
    Wrapper class for directed graphs.
    Internally uses :class:`nx.DiGraph` as a data structure.
    """
    def __init__(self):
        """Constructor."""
        self._internal_graph = nx.DiGraph()

    def add_nodes(self, node_list):
        """
        Adds nodes from the supplied iterable to the graph.

        :param node_list: An iterable containing the nodes to add.
        """
        for node in node_list:
            self._internal_graph.add_node(node)

    def add_edge(self, v_from, v_to, capacity):
        """
        Adds a directed edge between two vertices with the supplied capacity.

        :param v_from: The number of the node to start the edge in.
        :type v_from: int
        :param v_to: The number of the node to end the edge in.
        :type v_to: int
        :param capacity: The capacity of the edge to be added.
        :type capacity: int
        """
        self._internal_graph.add_edge(v_from, v_to, capacity=capacity)

    def maximum_flow(self, s, t):
        """
        Calculates the maximum flow in the network graph.

        :param s: The number of the source node.
        :type s: int
        :param t: The number of the sink node.
        :type t: int
        :return: A tuple consisting of:

            1. the value of the maximum flow,
            2. a :class:`Flow` object containing the flow values on the graph's edges.
        :rtype: tuple
        """
        max_flow_value, max_flow = edmonds_karp(self._internal_graph, s, t)
        return max_flow_value, Flow(max_flow)


class Flow:
    """
    Represents the values of the maximum flow computed by the :method:`Graph.maximum_flow` method.
    """
    def __init__(self, flow_dict):
        """
        Constructor.

        :param flow_dict: The dictionary containing the edge-to-flow-value mappings.
        :type flow_dict: dict
        """
        self._flow_dict = flow_dict

    def get_flow_value(self, v_from, v_to):
        """
        Returns the flow value for the edge running between two supplied vertices.

        :param v_from: The start vertex for the edge.
        :type v_from: int
        :param v_to: The end vertex for the edge.
        :type v_to: int
        :return: The value of the flow on the given edge.
        :rtype: int
        """
        return self._flow_dict[v_from][v_to]
