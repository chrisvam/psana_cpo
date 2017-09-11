from glob import glob
import os
#runs = range(95,115)
runs = range(108,109)
merge_chunks = False
smd = True

oldpath='/reg/d/psdm/cxi/cxid9114/xtc/'
newpath='/reg/d/psdm/cxi/cxid9114/demo/xtc'
if smd:
    oldpath = os.path.join(oldpath,'smalldata')
    newpath = os.path.join(newpath,'smalldata')

for r in runs:
    files = glob(os.path.join(oldpath,'*r'+('%4.4d*'%r)))
    for stream in range(5):
        streamstring = 's0'+str(stream)
        streamfiles = [f for f in files if streamstring in f]
        streamfiles.sort()
        if merge_chunks:
            fstring = ' '.join(streamfiles)
            outfname=os.path.split(streamfiles[0])[-1]
            cmd = 'bsub -q psanaq -o /reg/neh/home/cpo/junk/logs/%J.log /reg/neh/home/cpo/build/pdsdata/bin/xtcfilter -t /reg/neh/home/cpo/exafel/demo/hit_timestamps.txt -f '+fstring+' -o '+os.path.join(newpath,outfname)+' -i 0xac151a26 0xac151a9a'
            os.system(cmd)
        else:
            for f in streamfiles:
                fname=os.path.split(f)[-1]
                cmd = 'bsub -q psanaq -o /reg/neh/home/cpo/junk/logs/%J.log /reg/neh/home/cpo/build/pdsdata/bin/xtcfilter -t /reg/neh/home/cpo/exafel/demo/hit_timestamps.txt -f '+f+' -o '+os.path.join(newpath,fname)+' -i 0xac151a8d'
                print cmd
                os.system(cmd)
