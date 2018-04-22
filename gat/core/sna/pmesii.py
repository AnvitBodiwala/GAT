# import packages
import networkx as nx
import numpy as np
import pandas as pd

# import csv or xlsx into pandas
dataFrameList = (pd.read_excel("World Bank Data Iran.xlsx"),
                 pd.read_excel("CIRI Iran.xlsx"),
                 pd.read_excel("DPI Iran.xlsx"))
df = pd.concat(dataFrameList)
headerList = df.columns.values.tolist()
iran = df.to_dict(orient='index')

# initiali]ze iterative lists
attrList = []
edgeList = []
initList = []
y = len(iran)
# iterate through data set and assign PMESII points to weighted edge lists
for x in range(0, y):
    edgeList.append((iran[x]['Variable Code'], iran[x]['Domain']))
    edgeList.append((iran[x]['Domain'], 'PMESII Resources'))
    for y in range(1975, 1979):
        if iran[x][y] != str(iran[x][y]):
            initList.append(iran[x][y])
            attrList.append((iran[x]['Variable Code'], iran[x]['Domain'], np.mean(initList)))
            initList = []

# create network and graph
G = nx.Graph()
G.add_weighted_edges_from(attrList, 'W')


# construct baseline task models over PMESII network
tmEdgeList_1 = [('IC.IMP.TMDC',       'TM.VAL.MMTL.ZS.UN', -G['Economic']['IC.IMP.TMDC']['W']),
                ('IC.IMP.TMBC',       'TM.VAL.MMTL.ZS.UN', -G['Economic']['IC.IMP.TMBC']['W']),
                ('IC.IMP.CSDC.CD',    'TM.VAL.MMTL.ZS.UN', -G['Economic']['IC.IMP.CSDC.CD']['W']),
                ('IC.IMP.CSBC.CD',    'TM.VAL.MMTL.ZS.UN', -G['Economic']['IC.IMP.CSBC.CD']['W']),
                ('TM.VAL.MMTL.ZS.UN', 'NV.IND.MANF.CD',     G['Economic']['TM.VAL.MMTL.ZS.UN']['W']),
                ('SL.IND.EMPL.ZS',    'NV.IND.MANF.CD',     G['Economic']['SL.IND.EMPL.ZS']['W']),
                ('NV.IND.TOTL.KD.ZG', 'NV.IND.MANF.CD',     G['Economic']['NV.IND.TOTL.KD.ZG']['W']),
                ('SL.TLF.TOTL.IN',    'NV.IND.MANF.CD',     G['Economic']['SL.TLF.TOTL.IN']['W']),
                ('NV.IND.MANF.CD',    'IS.RRS.GOOD.MT.K6',  G['Economic']['NV.IND.MANF.CD']['W']),
                ('BM.GSR.TRAN.ZS',    'IS.RRS.GOOD.MT.K6',  G['Economic']['BM.GSR.TRAN.ZS']['W']),
                ('IS.AIR.GOOD.MT.K1', 'IS.RRS.GOOD.MT.K6',  G['Infrastructure']['IS.AIR.GOOD.MT.K1']['W']),
                ('IS.AIR.DPRT',       'IS.RRS.GOOD.MT.K6',  G['Infrastructure']['IS.AIR.DPRT']['W']),
                ('IS.RRS.GOOD.MT.K6', 'MS.MIL.XPRT.KD',     G['Infrastructure']['IS.RRS.GOOD.MT.K6']['W']),
                ('IC.EXP.DURS',       'MS.MIL.XPRT.KD',    -G['Economic']['IC.EXP.DURS']['W']),
                ('IC.EXP.DOCS',       'MS.MIL.XPRT.KD',    -G['Economic']['IC.EXP.DOCS']['W']),
                ('IC.EXP.COST.CD',    'MS.MIL.XPRT.KD',    -G['Economic']['IC.EXP.COST.CD']['W'])]

VC_1 = nx.DiGraph()
VC_1.add_weighted_edges_from(tmEdgeList_1)
aspl_1 = nx.average_shortest_path_length(VC_1, weight='W')
print(aspl_1)

tmEdgeList_2 = [('BX.GRT.TECH.CD.WD', 'BX.GRT.EXTA.CD.WD', G['BX.GRT.TECH.CD.WD']['Economic']['W']),
                ('SP.POP.TECH.RD.P6', 'BX.GRT.EXTA.CD.WD', G['SP.POP.TECH.RD.P6']['Societal']['W']),
                ('SP.POP.SCIE.RD.P6', 'BX.GRT.EXTA.CD.WD', G['SP.POP.SCIE.RD.P6']['Societal']['W']),
                ('BX.GRT.EXTA.CD.WD', 'NV.IND.MANF.CD',    G['BX.GRT.EXTA.CD.WD']['Economic']['W']),
                ('SL.IND.EMPL.ZS',    'NV.IND.MANF.CD',    G['SL.IND.EMPL.ZS']['Economic']['W']),
                ('NV.IND.TOTL.KD.ZG', 'NV.IND.MANF.CD',    G['NV.IND.TOTL.KD.ZG']['Economic']['W']),
                ('SL.TLF.TOTL.IN',    'NV.IND.MANF.CD',    G['SL.TLF.TOTL.IN']['Economic']['W']),
                ('NV.IND.MANF.CD',    'IS.RRS.GOOD.MT.K6', G['NV.IND.MANF.CD']['Economic']['W']),
                ('BM.GSR.TRAN.ZS',    'IS.RRS.GOOD.MT.K6', G['BM.GSR.TRAN.ZS']['Economic']['W']),
                ('IS.AIR.GOOD.MT.K1', 'IS.RRS.GOOD.MT.K6', G['IS.AIR.GOOD.MT.K1']['Infrastructure']['W']),
                ('IS.AIR.DPRT',       'IS.RRS.GOOD.MT.K6', G['IS.AIR.DPRT']['Infrastructure']['W']),
                ('IS.RRS.GOOD.MT.K6', 'TX.VAL.TECH.CD',    G['IS.RRS.GOOD.MT.K6']['Infrastructure']['W']),
                ('IC.EXP.DURS',       'TX.VAL.TECH.CD',   -G['IC.EXP.DURS']['Economic']['W']),
                ('IC.EXP.DOCS',       'TX.VAL.TECH.CD',   -G['IC.EXP.DOCS']['Economic']['W']),
                ('IC.EXP.COST.CD',    'TX.VAL.TECH.CD',   -G['IC.EXP.COST.CD']['Economic']['W'])]

VC_2 = nx.DiGraph()
VC_2.add_weighted_edges_from(tmEdgeList_2)
aspl_2 = nx.average_shortest_path_length(VC_2, weight='W')
print(aspl_2)

tmEdgeList_3 = [('NE.IMP.GNFS.CD',    'TM.VAL.SERV.CD.WT',  G['NE.IMP.GNFS.CD']['Economic']['W']),
                ('BM.GSR.MRCH.CD',    'TM.VAL.SERV.CD.WT',  G['BM.GSR.MRCH.CD']['Economic']['W']),
                ('TM.VAL.SERV.CD.WT', 'NV.IND.MANF.CD',     G['TM.VAL.SERV.CD.WT']['Economic']['W']),
                ('SL.IND.EMPL.ZS',    'NV.IND.MANF.CD',     G['SL.IND.EMPL.ZS']['Economic']['W']),
                ('NV.IND.TOTL.KD.ZG', 'NV.IND.MANF.CD',     G['NV.IND.TOTL.KD.ZG']['Economic']['W']),
                ('SL.TLF.TOTL.IN',    'NV.IND.MANF.CD',     G['SL.TLF.TOTL.IN']['Economic']['W']),
                ('NV.IND.MANF.CD',    'IS.RRS.GOOD.MT.K6',  G['NV.IND.MANF.CD']['Economic']['W']),
                ('BM.GSR.TRAN.ZS',    'IS.RRS.GOOD.MT.K6',  G['BM.GSR.TRAN.ZS']['Economic']['W']),
                ('IS.AIR.GOOD.MT.K1', 'IS.RRS.GOOD.MT.K6',  G['IS.AIR.GOOD.MT.K1']['Infrastructure']['W']),
                ('IS.AIR.DPRT',       'IS.RRS.GOOD.MT.K6',  G['IS.AIR.DPRT']['Infrastructure']['W']),
                ('IS.RRS.GOOD.MT.K6', 'TX.VAL.MANF.ZS.UN',  G['IS.RRS.GOOD.MT.K6']['Infrastructure']['W']),
                ('IC.EXP.DURS',       'TX.VAL.MANF.ZS.UN', -G['IC.EXP.DURS']['Economic']['W']),
                ('IC.EXP.DOCS',       'TX.VAL.MANF.ZS.UN', -G['IC.EXP.DOCS']['Economic']['W']),
                ('IC.EXP.COST.CD',    'TX.VAL.MANF.ZS.UN', -G['IC.EXP.COST.CD']['Economic']['W'])]

VC_3 = nx.DiGraph()
VC_3.add_weighted_edges_from(tmEdgeList_3)
aspl_3 = nx.average_shortest_path_length(VC_3, weight='W')
print(aspl_3)







