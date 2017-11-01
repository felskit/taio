import networkx as nx


def edmonds_karp(G, s, t):
    R = build_residual_network(G)
    for u in R:
        for e in R[u].values():
            e['flow'] = 0
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
    R = copy_digraph(G)
    edge_list = [(u, v) for u, v in G.edges()]
    for u, v in edge_list:
        R.add_edge(v, u, capacity=0)
    return R


def copy_digraph(G):
    inf = float('inf')
    H = nx.DiGraph()
    H.add_nodes_from(G)
    edge_list = [(u, v, attr) for u, v, attr in G.edges(data=True)]
    for u, v, attr in edge_list:
        c = attr.get('capacity', inf)
        H.add_edge(u, v, capacity=c)
    return H


def find_augmenting_path(G, s, t):
    q = [[s]]
    while q:
        vertex_path = q.pop(0)
        u = vertex_path[-1]
        if u == t:
            return construct_path(vertex_path)
        for u, v, attr in G.edges(u, data=True):
            if attr.get('capacity', float('inf')) > 0:
                new_vertex_path = list(vertex_path)
                new_vertex_path.append(v)
                q.append(new_vertex_path)


def construct_path(vertex_path):
    edges_path = []
    u = vertex_path[0]
    for v in vertex_path[1:]:
        edges_path.append((u, v))
        u = v
    return edges_path


def build_flow_dict(G, R):
    flow_dict = {}
    for u in G:
        flow_dict[u] = dict((v, 0) for v in G[u])
        flow_dict[u].update((v, attr['flow']) for v, attr in R[u].items() if attr['flow'] > 0)
    return flow_dict
