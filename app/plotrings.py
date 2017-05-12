
from psana import *
import Image
import matplotlib.pyplot as plt

setConfigFile('plotrings.cfg')
evt = DataSource('exp=cxib2313:run=115').events().next()
max = evt.get(ndarray_float64_2, Source('DetInfo(CxiDs1.0:Cspad.0)'), 'image0')
print max.shape
plt.figure('cspad max')
plt.imshow(max)
plt.show()
