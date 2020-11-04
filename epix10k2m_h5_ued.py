from psana import *
import subprocess
import numpy as np
from psmon import publish
from psmon.plots import Image
publish.local = True
publish.plot_opts.aspect = 1

ds = MPIDataSource('exp=mfxc00118:run=71:smd')
epix = Detector('epix10k2M')
smldata = ds.small_data('epix10k2M_ued.h5',gather_interval=1)

for nevt,evt in enumerate(ds.events()):
   raw = epix.image(evt)
   print(raw.shape)
   if raw is None:
      print(nevt,'None')
      continue
   smldata.event(raw=raw[831:,801:])
   if nevt>100: break

imgsend = Image(0,"Random",raw[:855,855:])
publish.send('image',imgsend)
raw_input("hit cr")

smldata.save()
