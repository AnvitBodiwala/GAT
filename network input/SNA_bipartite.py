import networkx as nx
from networkx.algorithms import bipartite as bi
# import csv, might deveop in order to read bith xlsx and csv
import xlrd
import matplotlib.pyplot as plt
import jgraph

class SNA():

    def __init__(self,excel_file, sheet):
        self.header, self.list = self.readFile(excel_file, sheet)
        self.G = nx.complete_multipartite_graph()
        self.nodes = []
        self.edges = []
        self.nodeSet = []
        self.clustering_dict = {}
        self.latapy_clustering_dict = {}
        self.closeness_centrality_dict = {}
        self.betweenness_centrality_dict = {}
        self.degree_centrality_dict = {}

    # Read xlsx file and save the header and all the rows (vector) containing features
    # Input: xlsx file, sheet

    def readFile(self, excel_file, sheet):
        workbook = xlrd.open_workbook(excel_file)
        sh = workbook.sheet_by_name(sheet)
        header = [sh.cell(0,col).value.strip("\n") for col in range(sh.ncols)]
        New_ncols = sh.ncols - 1

        # If any, delete all the emtpy features in the header
        while header[New_ncols] == '':
            header.remove(header[New_ncols])
            New_ncols -= 1

        list = []
        for row in range(1,sh.nrows):
            tempList = []
            for col in range(New_ncols + 1):
                if type(sh.cell(row,col).value) == type(""):
                    tempList.append(sh.cell(row,col).value.strip("\n"))
                else:
                    tempList.append(sh.cell(row,col).value)
            list.append(tempList)

        return header,list


    #create set of nodes for bipartite graph
    # name = names of the node. This is defined by the header. ex: Abbasi-Davani.F: Name  or Abbasi-Davani.F: Faction leader
    # nodeSet = names that define a set of node. For example, we can define Person, Faction Leader, and Party Leader as "Agent"
    # note: len(name) = len(nodeSet), else code fails

    def createNodeList(self, name, nodeSet):
        header, list = self.header, self.list          #need to use header for role analysis
        counter = 0                                    #counter for the nodeSet
        self.nodeSet = nodeSet
        for feature in name:
            nodeList = []
            for row in list:
                if row[feature] != '':
                    if row[feature] not in nodeList:
                        nodeList.append(row[feature])
            self.G.add_nodes_from(nodeList, bipartite = nodeSet[counter])
            counter+=1
        self.nodes = nx.nodes(self.G)

    #create a list of edges that connect among sets
    #This part is currently still testing.
    #Right now trying to see if the graph is displayed successfully, but later on need to add a argument that passes the
    #list of features that we want the graph to display in bipartite

    def createEdgeList(self, featureList):
        list = self.list
        edgeList = []
        for row in list:
            for i in range(len(featureList)):
                for j in range(len(featureList) - 1):
                    if (row[featureList[i]] != '' and row[featureList[j]] != '') and (row[featureList[i]] != row[featureList[j]]):
                        edgeList.append((row[featureList[i]],row[featureList[j]]))
        self.G.add_edges_from(edgeList)
        self.edges = edgeList

    def addEdges(self, pair):
        data = self.list
        newEdgeList = []
        for row in data:
            if (row[pair[0]] != '' and row[pair[1]] != '') and (row[pair[0]] != row[pair[1]]):
                newEdgeList.append((row[pair[0]], row[pair[1]]))
        self.G.add_edges_from(newEdgeList)
        self.edges.extend(newEdgeList)


    # Getter for nodes and edges
    def getNodes(self):
        return self.nodes

    def getEdges(self):
        return self.edges

    # Find clustering coefficient for each nodes
    def clustering(self):
        self.clustering_dict = bi.clustering(self.G)

    # set lapaty clustering to empty dictionary if there are more then 2 nodesets
    # else return lapaty clustering coefficients for each nodes
    def latapy_clustering(self):
        if len(self.nodeSet) != 2 or len(set(self.nodeSet)) != 2:
            self.latapy_clustering_dict = {}
        else:
            self.latapy_clustering_dict = bi.latapy_clustering(self.G)

    def robins_alexander_clustering(self):
        self.robins_alexander_clustering_dict = bi.robins_alexander_clustering(self.G)

    # Find closeness_centrality coefficient for each nodes
    def closeness_centrality(self):
        self.closeness_centrality_dict = bi.closeness_centrality(self.G, self.nodes)

    # Find degree_centrality coefficient for each nodes
    def degree_centrality(self):
        self.degree_centrality_dict = nx.degree_centrality(self.G)

    # Find betweenness_centrality coefficient for each nodes
    def betweenness_centrality(self):
        self.betweenness_centrality_dict = nx.betweenness_centrality(self.G)


    def get_clustering(self, lst=[]):
        if len(lst) == 0:
            return self.clustering_dict
        else:
            sub_dict = {}
            for key,value in self.clustering_dict:
                if key in lst:
                    sub_dict[key] = value
            return sub_dict

    def get_latapy_clustering(self, lst=[]):
        if len(lst) == 0:
            return self.latapy_clustering_dict
        else:
            sub_dict={}
            for key, value in self.latapy_clustering_dict:
                if key in lst:
                    sub_dict[key] = value
            return sub_dict

    def get_robins_alexander_clustering(self, lst=[]):
        if len(lst) == 0:
            return self.robins_alexander_clustering_dict
        else:
            sub_dict={}
            for key, value in self.robins_alexander_clustering_dict:
                if key in lst:
                    sub_dict[key] = value
            return sub_dict

    def get_closeness_centrality(self, lst=[]):
        if len(lst) == 0:
            return self.closeness_centrality_dict
        else:
            sub_dict = {}
            for key, value in self.closeness_centrality_dict:
                if key in lst:
                    sub_dict[key] = value
            return sub_dict

    def get_degree_centrality(self, lst=[]):
        if len(lst) == 0:
            return self.degree_centrality_dict
        else:
            sub_dict = {}
            for key, value in self.degree_centrality_dict:
                if key in lst:
                    sub_dict[key] = value
            return sub_dict

    def get_betweenness_centrality(self, lst=[]):
        if len(lst) == 0:
            return self.betweenness_centrality_dict
        else:
            sub_dict = {}
            for key, value in self.betweenness_centrality_dict:
                if key in lst:
                    sub_dict[key] = value
            return sub_dict


    # draw 2D graph
    # attr is a dictionary that has color and size as its value.

    def graph_2D(self, attr, label=False):
        bipartite = nx.get_node_attributes(self.G, 'bipartite')
        Nodes = nx.nodes(self.G)
        pos = nx.spring_layout(self.G)
        labels = {}

        for node in bipartite:
            labels[node] = node

        for node in set(self.nodeSet):
            nx.draw_networkx_nodes(self.G, pos,
                                   with_labels=False,
                                   nodelist = [n for n in Nodes if bipartite[n] == node],
                                   node_color = attr[node][0],
                                   node_size = attr[node][1],
                                   alpha=0.8)

        nx.draw_networkx_edges(self.G, pos, width=1.0, alpha=0.5)

        for key,value in pos.items():
            pos[key][1] += 0.01

        if label == True:
            nx.draw_networkx_labels(self.G, pos, labels, font_size=8)

        limits=plt.axis('off')
        plt.show()

    #draw 3 dimensional verison of the graph (returning html object)

    def graph_3D(self):
        n = nx.edges(self.G)
        removeEdge=[]
        for i in range(len(n)):
            if n[i][0] == '' or n[i][1] == '':
                removeEdge.append(n[i])
        for j in range(len(removeEdge)):
            n.remove(removeEdge[j])
        jgraph.draw(nx.edges(self.G), directed="false")



############
####TEST####
############

# Graph = SNA("iran.xlsx", "2011")
# Graph.createNodeList([1,4], ["Agent", "Institution"])
# Graph.createEdgeList([1,4])
# test = Graph.getNodes()
# Graph.graph_2D({"Agent":['y',50], "Institution":['b',50]}, label=True)
# Graph.clustering()
# Graph.latapy_clustering()
# Graph.robins_alexander_clustering()
# Graph.closeness_centrality()
# Graph.betweenness_centrality()
# Graph.degree_centrality()
# print(Graph.get_clustering())
# print(Graph.get_closeness_centrality())
# print(Graph.get_betweenness_centrality())
# print(Graph.get_degree_centrality())
# print(Graph.get_latapy_clustering())
# print(Graph.get_robins_alexander_clustering())


