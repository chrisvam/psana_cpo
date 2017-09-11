from psana import *
import time

testtime = str(20140615213913346)

ds = DataSource('exp=cxid9114:run=95:smd:stream=0-79')

for nevt,evt in enumerate(ds.events()):
    id = evt.get(EventId)
    t = id.time()
    ms = "%03d" % (t[1]/1000000)
    tstring = time.strftime("%Y%m%d%H%M%S", time.gmtime(t[0])) + ms
    if testtime == tstring:
        print testtime
        break
