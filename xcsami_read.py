from psana import DataSource
ds = DataSource(files='xcsami.xtc2')
myrun = next(ds.runs())
det = myrun.Detector('xpp_ipm4')
for evt in myrun.events():
    print(det.raw.sum(evt))
