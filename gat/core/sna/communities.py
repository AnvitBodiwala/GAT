import networkx as nx
import scipy as sp
from community import best_partition
from collections import defaultdict


def find_cliques(G, centralities, filter="BEL"):
    cliquesList = []
    # Find central nodes
    scaled = list(sp.stats.zscore(centralities.get(node) for node in G.nodes()))
    for i in range(len(scaled)):
        scaled[i] = (G.nodes()[i], scaled[i])
    selected = [key for key, val in scaled if
                filter in key]  # used z-score for top 20th percentile, temporary change to only show beliefs
    for centralNode in selected:
        sub_G = nx.DiGraph()
        find_subgraph(G, centralNode, sub_G, 3)
        if len(list(sub_G.nodes())) > 5:
            cliquesList.append(sub_G.to_undirected())
    return cliquesList, selected

# Make subgraphs from central nodes
def find_subgraph(G, centralNode, subGraph, depth):
    nodeList = [(centralNode, target) for target in G.neighbors(centralNode)]
    subGraph.add_edges_from(nodeList)
    if depth > 0:
        for ancillary in G.neighbors(centralNode):
            find_subgraph(G, ancillary, subGraph, depth - 1)

def louvain(G, weightKey='emoWeight', centralities=None):
    # use partition argument to start the algorithm with a particular partition, i.e. the find_cliques method?
    partition = best_partition(G, weight=weightKey)
    partitions = defaultdict(list)
    partitionLists = []
    centralNodes = []
    subgraphs = []
    if centralities is not None:
        for node, partitionKey in partition.items():
            partitions[partitionKey].append(node)
            partitionLists = [nodes for partition, nodes in partitions.items()]
        for nodes in partitionLists:
            core_nodes = [node for node in nodes if G.node[node].get("ontClass") in ["Belief","Symbol","Event","Role"]]
            partitionCentralities = {node: centralities[node] for node in core_nodes}
            if len(core_nodes) > 1: #if core complex exists...
                centralNodes.append( max(partitionCentralities, key=partitionCentralities.get) ) #choose label from core complex
                subgraphs.append(G.subgraph(nodes)) #append full subgraph
        return subgraphs, centralNodes

    else:
        return "No centralities passed"

