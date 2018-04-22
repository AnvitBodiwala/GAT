import networkx as nx
import random
import scipy as sp

from gat.core.sna import ergm


def resilience(cliques_found, ergm_iters=3000):
    scaledResilience = {}
    scaledBaseline = {}
    toScale = []
    baselinesToScale = []
    traces = []
    formatted_traces = {}
    cliques, selected = cliques_found
    # Find resilience of subgraphs
    for clique in cliques:
        initShortestPath = nx.average_shortest_path_length(clique)
        baselinesToScale.append(initShortestPath)
        # creating perturbation by removing random 10% of nodes and averaging result of x iterations
        G = clique.copy()  # percent of nodes removed can be changed here
        rSample = random.sample(G.nodes(), int(G.number_of_nodes() * 0.1))
        G.remove_nodes_from(rSample)
        coefs, new_trace = ergm.resilience(G, ergm_iters, mu=initShortestPath*.2)
        toScale.append(coefs["aspl"])
        traces.append(new_trace["aspl"].tolist())

    # scale resilience measures on a normal scale
    for i in range(len(cliques)):
        scaledResilience[selected[i]] = toScale[i]
        scaledBaseline[selected[i]] = sp.stats.percentileofscore(baselinesToScale, baselinesToScale[i])
        formatted_traces[selected[i]] = traces[i]

    return scaledBaseline, scaledResilience, formatted_traces
