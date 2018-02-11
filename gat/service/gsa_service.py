import csv
import json
#from xml.dom import minidom
from dbfread import DBF

from gat.core.gsa.misc import util, map_generator
from gat.core.gsa.core import spatial_dynamics, autocorrelation, weights, network, geojson, emotional_space
from gat.dao import dao


# TODO utilize temp dir

def tempParseGSA(GSA_file_CSV, GSA_file_SHP, idVar, nameVar):
    if GSA_file_CSV == None or GSA_file_SHP == None:
        return (None, None)

    gsaCSV = []
    with open(GSA_file_CSV) as csvfile:
        try:
            reader = csv.reader(csvfile)
            for row in reader:
                tempRow = [x.replace("'", "APOSTROPHE") for x in row]
                gsaCSV.append(tempRow)
        except:
            return (None, True)

    #TODO: remove this
    gsaSVG = "out/gsa/mymap.svg"
    generateMap(GSA_file_SHP, gsaSVG)

    with open(gsaSVG, 'r') as myfile:
        data = None
        try:
            data = myfile.read()
        except:
            return (None, True)
    data = data.replace('"', "'")
    nameMapping = util.getNameMapping(gsaSVG, idVar, nameVar)
    nameMapping = {key: value.replace("'", "APOSTROPHE") for key, value in nameMapping.items()}
    return json.dumps(str(gsaCSV).replace('"', "'")), json.dumps(data), json.dumps(str(nameMapping).replace('"', "'"))

def generateMap(GSA_file_SHP, path):
    map_generator.generateMap(GSA_file_SHP, path)

def getColumns(path):
    return DBF(path).field_names

def getNameMapping(path, nameVar):
    return [record[nameVar] for record in DBF(path).records]

def parseGSA(GSA_file_CSV, GSA_file_SVG):
    if GSA_file_CSV == None or GSA_file_SVG == None:
        print("csv or svg is none")
        return (None, None)

    gsaCSV = []
    with open(GSA_file_CSV) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            gsaCSV.append(row)

    with open(GSA_file_SVG, 'r') as myfile:
        data = myfile.read()
    data = data.replace('"', "'")
    return json.dumps(gsaCSV), json.dumps(data)


def runGSA(case_num, autocorrelationRows, autocorrelationCols, sdRows, sdCols, idVariable):
    fileDict = dao.getFileDict(case_num)
    observations = weights.extractObservations(fileDict['GSA_Input_CSV'], autocorrelationRows, autocorrelationCols)
    w = weights.generateWeightsUsingShapefile(fileDict['GSA_Input_SHP'], idVariable=idVariable)
    globalAutoCorrelation = autocorrelation.globalAutocorrelation(observations, w)
    localAutoCorrelation = autocorrelation.localAutocorrelation(observations, w)
    observations = weights.extractObservations(fileDict['GSA_Input_CSV'], sdRows, sdCols)
    spatialDynamics = spatial_dynamics.markov(observations, w, method="spatial")
    return localAutoCorrelation, globalAutoCorrelation, spatialDynamics

def geoNetwork(case_num):
    fileDict = dao.getFileDict(case_num)
    #outputShape = network.create_network(fileDict['Geonet_Input_Streets'], fileDict['Geonet_Input_Crimes'])
    outputShape = fileDict['Geonet_Input_Streets']
    #geojson.convert(outputShape + '.shp')
    print("IN HERE")
    geojson.convert(outputShape)
    #can modify filedict in here so that you can access the files in visualization.py
    #call ur code in here

    return fileDict

def emoSpace(case_num):

    actors, relations = emotional_space.getRelations()
    #can modify filedict in here so that you can access the files in visualization.py
    #call ur code in here
    return actors, relations