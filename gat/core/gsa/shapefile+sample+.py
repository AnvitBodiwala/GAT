
# coding: utf-8

# In[48]:

import shapefile as shp
from matplotlib import pyplot as plt

#get_ipython().magic('matplotlib inline')


# In[66]:

filepath = '/Users/anvitb/Projects/GAT/gat/core/gsa/core/mygeodata/sample'
w = shp.Writer(shp.POLYGON)
w.poly(parts=[[[1,5],[5,5],[5,1],[3,3],[1,1]]])
w.field('FIRST_FLD','C','40')
w.field('SECOND_FLD','C','40')
w.record('First','Polygon')

# w = shp.Writer(shapeType=3)
#  w.field("field1", "C")
# w.field("field2", "C")
# w.record("row", "one")
# w.record("row", "two")
# w.point(1, 1)
# w.point(2, 2)
# print ('test1')
# w.line(parts=[[[1,5],[5,5],[5,1],[3,3],[1,1]]])
# print ('test2')
# w.line(parts=[[[2,7],[0,8],[1,1],[3,3],[4,7]]])
# print ('test3')
# w.poly(parts=[[[1,3],[5,3]]], shapeType=shp.POLYLINE)
w.save(filepath)
'''
plt.figure()
sf = shp.Reader(filepath)
for shape in list(sf.iterShapes()):
    #print(shape.points)
    
    x = [i[0] for i in shape.points]
    y = [i[1] for i in shape.points]
    plt.plot(x,y)
    
plt.show()
'''

# In[ ]:




# In[ ]:



