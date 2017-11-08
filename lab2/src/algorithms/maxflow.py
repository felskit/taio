import networkx as nx
from queue import deque


def edmonds_karp(G, s, t):
    """
    An implementation of the Edmonds-Karp maximum flow algorithm.

    :param G: The network graph in which to find the maximum flow.
    :type G: nx.DiGraph
    :param s: The source node in the network.
    :type s: int
    :param t: The sink node in the network.
    :type t: int
    :return: A tuple containing:

             - the maximum flow value,
             - a dictionary containing the flow values on all of the graph's edges.
    :rtype: tuple
    """
    R = build_residual_network(G)
    for u in R:
        for v in R[u]:
            R[u][v]['flow'] = 0
    flow_value = 0

    while True:
        edges_path = find_augmenting_path(R, s, t)
        if not edges_path:
            break

        df = float('inf')
        for u, v in edges_path:
            if R[u][v]['capacity'] < df:
                df = R[u][v]['capacity']
        for u, v in edges_path:
            R[u][v]['flow'] += df
            R[u][v]['capacity'] -= df
            R[v][u]['capacity'] += df
        flow_value += df

    return flow_value, build_flow_dict(G, R)


def build_residual_network(G):
    """
    Initializes an empty residual network for the network graph *G*.

    :param G: The graph for which to build the residual network.
    :type G: nx.DiGraph
    :return: An empty residual network with the edges from the original network, and added edges in the other
    direction with capacity 0.
    :rtype: nx.DiGraph
    """
    R = copy_digraph(G)
    edge_list = [(u, v) for u, v in G.edges()]
    for u, v in edge_list:
        R.add_edge(v, u, capacity=0)
    return R


def copy_digraph(G):
    """
    Makes a copy of the supplied graph *G*.

    :param G: The graph instance to be copied.
    :type G: nx.DiGraph
    :return: A copy of the supplied graph.
    :rtype: nx.DiGraph
    """
    inf = float('inf')
    H = nx.DiGraph()
    H.add_nodes_from(G)
    edge_list = [(u, v, attr) for u, v, attr in G.edges(data=True)]
    for u, v, attr in edge_list:
        c = attr.get('capacity', inf)
        H.add_edge(u, v, capacity=c)
    return H


def find_augmenting_path(G, s, t):
    """
    Finds an augmenting path in the residual network *G*.

    :param G: The residual graph to find a path in.
    :type G: nx.DiGraph
    :param s: The number of the source node.
    :type s: int
    :param t: The number of the sink node.
    :type t: int
    :return: - If a path exists, the function returns the path as a list of vertices.
             - If the path does not exist, the function returns None.
    :rtype: list
    """
    q = deque([s])
    visited = [False] * len(G.nodes)
    visited[s] = True
    parent = {s: None}

    # could be refactored to build edges_path instead of building vertex_path (and using construct_path later)
    def trace_path():
        vertex_path = [t]
        while vertex_path[-1] != s:
            vertex_path.append(parent[vertex_path[-1]])
        vertex_path.reverse()
        return construct_path(vertex_path)

    while q:
        u = q.popleft()
        if u == t:
            return trace_path()
        for _, v, attr in G.edges(u, data=True):
            if (not visited[v]) and attr.get('capacity', float('inf')) > 0:
                visited[v] = True
                parent[v] = u
                q.append(v)


def construct_path(vertex_path):
    """
    For a list containing vertices of a path, returns the edges of that path.

    :param vertex_path: The list of vertices of a path.
    :type vertex_path: list
    :return: The list of edges on the supplied path.
    :rtype: list
    """
    edges_path = []
    u = vertex_path[0]
    for v in vertex_path[1:]:
        edges_path.append((u, v))
        u = v
    return edges_path


def build_flow_dict(G, R):
    """
    Upon completion of the Edmonds-Karp algorithm, this function collects the values of the maximum flow
    on all edges of the networks into a dictionary.

    :param G: The original network graph for which to find the maximum flow.
    :type G: nx.DiGraph
    :param R: The residual network for the graph *G*.
    :type R: nx.DiGraph
    :return: A nested dictionary containing flow values for all edges in the graph.
             To access the value of the flow on an edge *uv*, access the value ``flow_dict[u][v]``.
    :rtype: dict
    """
    flow_dict = {}
    for u in G:
        flow_dict[u] = dict((v, 0) for v in G[u])
        flow_dict[u].update((v, attr['flow']) for v, attr in R[u].items() if attr['flow'] > 0)
    return flow_dict
