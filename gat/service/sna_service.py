import copy

import matplotlib
import networkx as nx
import xlsxwriter as xlsxw

from gat.dao import dao

colors = ["DeepSkyBlue", "Gold", "ForestGreen", "Ivory", "DarkOrchid", "Coral", "DarkTurquoise", "DarkCyan", "Blue"]
hexColors = {}
for color in colors:
    rgbVal = matplotlib.colors.colorConverter.to_rgb(color)
    hexVal = matplotlib.colors.rgb2hex(rgbVal).replace("#", "0x")
    hexColors[color] = hexVal


def SNA2Dplot(graph, request, label=False):
    attr = {}
    if graph == None:
        return None
    if request.form.get("options") == None:
        i = 0
        for nodeSet in graph.classList:
            attr[nodeSet] = [colors[i], 50]
            i += 1
            if i > len(colors) + 1:
                i = 0
    else:
        for nodeSet in graph.classList:
            c = request.form.get(nodeSet + "Color")
            attr[nodeSet] = [c, 50]

    return graph.plot_2D(attr, label=label)


# makes more sense to make a whole SNA viz method that outputs both 2D and 3D if so desired
# 2D is probably not desired in any case though
def SNA2Dand3D(graph, request, case_num, _3D=True, _2D=False, label=False):
    fileDict = dao.getFileDict(case_num)
    systemMeasures = {}

    if graph == None:
        return None, None, None, None

    # make both
    attr = {}
    colorInput = []

    if request.form.get("options") == None:
        i = 0
        for nodeSet in graph.classList:
            attr[nodeSet] = [colors[i], 50]
            colorInput.append(hexColors[colors[i]])
            i += 1
            if i == 8:
                i = 0
    else:
        for nodeSet in graph.classList:
            attr[nodeSet] = [request.form.get(nodeSet + "Color"), 50]
            c = request.form.get(nodeSet + "Color")
            colorInput.append(hexColors[c])

    if request.form.get("removeNodeSubmit") != None:
        graph.removeNode(request.form.get("a"))

    # Get new node info, if available
    if request.form.get("addNodeSubmit") != None:

        node = request.form.get("nodeName")

        attrDict = {
            'block': request.form.get("classList"),
            'class': request.form.get("classList")
        }
        i = 0
        while (request.form.get("attribute" + str(i)) is not None) and (
                    request.form.get("attribute" + str(i)) != '') and (
                    request.form.get("value" + str(i)) is not None) and (
                    request.form.get("value" + str(i)) != ''):
            key = request.form.get("attribute" + str(i))
            value = request.form.get("value" + str(i))
            if request.form.get("weight" + str(i)) is not None and request.form.get("weight" + str(i)) != '':
                value = [value, {'W': request.form.get("weight" + str(i))}]
            dictForm = {key: value}
            attrDict.update(dictForm)
            i += 1

        links = []
        j = 0
        while request.form.get("link" + str(j)) != None:
            links.append(request.form.get("link" + str(j)))
            j += 1

        graph.addNode(node, attrDict, links)

    if request.form.get("eventSubmit") != None:
        fileDict['SNA_Events'] = 'static/sample/sna/suicide_attacks_subset.xlsx' ##TODO add a blueprint route for event sheet here
        inputFile = fileDict['SNA_Events']
        iters = int(request.form.get("iters"))
        systemMeasures['SentimentDict'] = True
        fileDict['SentimentChange'] = write_to_excel(graph.event_update(inputFile,iters))
        graph.calculatePropensities(fileDict["propToggle"])

    # Add system measures dictionary
    try:
        systemMeasures["Node Connectivity"] = graph.node_connectivity() # Currently only returning zero...
    except:
        "No node connectivity"
    try:
        systemMeasures["Average Clustering"] = graph.average_clustering()
    except:
        "No average clustering"
    # try:
    #     systemMeasures["Average Degree Connectivity"] = graph.average_degree_connectivity()
    # except:
    #     "No average degree connectivity"
    try:
        systemMeasures["Degree Assortativity"] = graph.degree_assortativity()
    except:
        "No degree assortativity"
    try:
        systemMeasures["Center"] = graph.center()
    except:
        "No center"
    try:
        systemMeasures["Diameter"] = graph.diameter()
    except:
        "No periphery"
    try:
        systemMeasures["Periphery"] = graph.periphery()
    except:
        "No periphery"
    systemMeasures["Overall Sentiment"] = graph.sentiment(types=["Belief","Audience","Actor"],key='W')
    # try:
    #     systemMeasures["Triadic Census"] = graph.triadic_census()
    # except:
    #     "No triadic census"

    # systemMeasures["Attribute Assortivity"] = graph.attribute_assortivity() # Which attributes...? UI?
    if graph.is_strongly_connected():
        systemMeasures["Connection Strength"] = "Strong"
    elif graph.is_weakly_connected():
        systemMeasures["Connection Strength"] = "Weak"

    # Add system measures descriptions to dictionary
    systemMeasures["Description"] = {
        'Average Clustering': 'A high clustering coefficient indicates that actors within the network are closely connected to a statistically significant degree. It is a sophisticated measure of the density of a network.',
        'Connection Strength': 'Knowing whether a graph is strongly or weakly connected is helpful because it demonstrates the robustness of the graph based on its redundancy. If a graph is strongly connected, there are two links between each actor in the network, one in each direction. A strongly connected graph thus would likely have more redundant communication/information flow and be more difficult to perturb than a weakly connected graph.',
        'Resilience': 'The baseline value for resilience is determined by perturbing each community in the network and measuring the mean shortest path average over several perturbations. The results are scaled on a normal curve across all cliques and a percentile resilience is determined for each clique. A high percentile resilience denotes resilience to perturbation. These values are visualized on a color spectrum from red to blue, where red is low relative resilience and blue is high relative resilience.',
        'AddNode': 'Introduces a new node to the network, complete with a user-defined name, user-defined attributes and known links. Using the DRAG link prediction model, node attributes are used to form likely connections and intelligently model the effects of external change on the network. New nodes and their predicted links are colored red for easy identification.',
        'RemoveNode': 'Removes the node inputted in the box below and any links to which it belongs.',
        'eigenvector': 'Centrality measure which sums the centralities of all adjacent nodes.',
        'betweenness': 'Centrality based on the shortest path that passes through the node.',
        'sentiment':'The sum of all actor sentiments towards this node.',
        'Overall Sentiment': 'The sum of all actor sentiments towards this node.',
        'Cliques':'Influence communities are  detected in two-step Louvain modularity optimization. First, the core myth-symbol complexes are identified and named. Second, very proximate actors are grouped with the myth-symbol complex to form a full influence network.',
        'EventAddition': 'Choose a number of iterations to simulate event addition into the network. Events are drawn from input file.',
    }

    # Find cliques when requested
    if request.form.get("cliqueSubmit") != None:
        cliques, names = graph.communityDetection()
        systemMeasures["Cliques"] = []
        fileDict["Cliques"] = []
        for name, clique in zip(names, cliques):
            central = graph.G.node[name].get('Name')[0] if graph.G.node[name].get('Name') is not None else name
            nodes = []
            json_clique = {}
            i = 0
            for node in clique.nodes():
                nodes.append(graph.G.node[node].get('Name')[0] if graph.G.node[node].get('Name') is not None else node)
                json_clique["node"+str(i)] = node
                i+=1
            systemMeasures["Cliques"].append((central,nodes))
            fileDict["Cliques"].append((central,json_clique))

    # Calculate resilience when requested
    if request.form.get("resilienceSubmit") != None:
        try:
            systemMeasures["Baseline"], systemMeasures["Resilience"], systemMeasures["Trace"] = graph.calculateResilience()  # gets a scaled resilience value for each clique identified in network
        except nx.exception.NetworkXError:
            systemMeasures["Resilience"] = "Could not calculate resilience, NetworkX error."

    copy_of_graph = copy.deepcopy(graph)
    fileDict['copy_of_graph'] = copy_of_graph
    # return based on inputs
    ret3D = graph.create_json(graph.classList, colorInput) if _3D else None
    label = True if not label and len(graph.nodes) < 20 else False
    ret2D = graph.plot_2D(attr, label) if _2D else None
    fileDict['jgdata'] = ret3D

    return ret3D, ret2D, attr, systemMeasures


def prep(graph):
    if graph != None and len(graph.G) > 0:
        if nx.algorithms.bipartite.is_bipartite(graph.G):
            graph.clustering()
        graph.closeness_centrality()
        graph.betweenness_centrality()
        graph.degree_centrality()
        # graph.katz_centrality()
        graph.eigenvector_centrality()
        graph.load_centrality()

def write_to_excel(ret):
    path = "out/sna/SentimentChange.xlsx"
    workbook = xlsxw.Workbook(path)
    for i in range(len(ret)):
        worksheet = workbook.add_worksheet(str(i))
        row = 0
        col = 0
        for header in ["Source","Target","Sentiment Change"]:
            worksheet.write(row,col,header)
            col += 1
        col = 0
        for line in ret[i]:
            row += 1
            worksheet.write(row, col, line.source)
            worksheet.write(row, col+1, line.target)
            worksheet.write(row, col+2, line.change)
    workbook.close()
    return path
