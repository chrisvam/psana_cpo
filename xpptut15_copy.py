import glob
import os
import shutil
import stat

import numpy as np
import os

class Dgram:
    def __init__(self,f):
        self._nwords = 10
        self._data = np.fromfile(f,dtype=np.uint32,count=self._nwords)
        self.f = f
    def write(self):
        self._data.tofile(self.f)
    def clocklow(self): return self._data[0]
    def clockhigh(self): return self._data[1]
    def tslow(self): return self._data[2]
    def tshigh(self): return self._data[3]
    def env(self): return self._data[4]
    def setenv(self,value): self._data[4]=value
    def dmg(self): return self._data[5]
    def srclog(self): return self._data[6]
    def srcphy(self): return self._data[7]
    def contains(self): return self._data[8]
    def extent(self): return self._data[9]
    def next(self): return self.extent()+5*4 # 5*4 is size of Xtc
    def data(self): return self._data

def fixRunNumber(fname):
    fstat = os.stat(fname).st_mode
    os.chmod(fname, fstat | stat.S_IWUSR)
    # to fix the run number in the "env" field of the beginrun datagram
    newrun = int(os.path.basename(fname).split('-')[1][1:])
    f = open(fname,'r+')
    configdg = Dgram(f)
    f.seek(configdg.next())
    beginrunoffset = f.tell()
    beginrundg = Dgram(f)
    f.seek(beginrunoffset)
    beginrundg.setenv(newrun)
    beginrundg.write()

    #check
    f.seek(beginrunoffset)
    newbeginrundg = Dgram(f)
    #print beginrundg.data()
    #print newbeginrundg.data()
    assert newbeginrundg.env()==newrun, 'Read incorrect run number %d %d'%(newrun,newbeginrundg.env())
    f.close()
    os.chmod(fname, fstat)

def safecopy(inf,outf):
    if not os.path.isfile(inf):
        print '*** Input file',inf,'does not exist. Not copied'
        return
    if os.path.isfile(outf):
        print '*** Output file',outf,'exists. Not copied'
        return
    print 'cp',inf,outf
    shutil.copyfile(inf,outf)
    return

# assumes just one set of constants for now, using the first run
def copyconstants(hutch,expt,inruns,outruns):
    from PSCalib.CalibFileFinder import CalibFileFinder
    cdir = os.path.join('/reg/d/psdm',hutch,expt,'calib')
    groupdirs = glob.glob(os.path.join(cdir,'*'))
    for groupdir in groupdirs:
        if ':' not in groupdir: continue # heuristic to avoid random dirs in calib/
        group = os.path.basename(groupdir)
        sourcedirs = glob.glob(os.path.join(groupdir,'*'))
        for sourcedir in sourcedirs:
            src = os.path.basename(sourcedir)
            typedirs = glob.glob(os.path.join(sourcedir,'*'))
            for typedir in typedirs:
                type = os.path.basename(typedir)
                cff = CalibFileFinder(cdir, group, pbits=0)
                inf = cff.findCalibFile(src, type, inruns[0])
                if inf is '':
                    print '*** No',type,'calibration constants found for exp=%s:run=%d. Constants not copied'%(expt,inruns[0])
                    continue
                outcdir = os.path.join(outtopdir,'calib',group,src,type)
                if not os.path.isdir(outcdir):
                    print '*** Creating directory',outcdir
                    os.makedirs(outcdir)
                outf = os.path.join(outcdir,'%d-%d.data'%(outruns[0],outruns[-1]))
                safecopy(inf,outf)

class exptruns:
    def __init__(self,expt,inruns,outruns_start):
        self.expt = expt
        self.inruns = inruns
        self.outruns_start = outruns_start

exptlist = []
#exptlist.append(exptruns('xppc0114',[287],160))
#exptlist.append(exptruns('xppc0115',[270],170))
#exptlist.append(exptruns('xppf2115',[189,190,192],180))
#exptlist.append(exptruns('xpp72213',[324,300],190))
#exptlist.append(exptruns('xppd0115',[375,366],200))
#exptlist.append(exptruns('xppi3815',[224,225],210))
#exptlist.append(exptruns('xppi3815',range(100,105),220))
#exptlist.append(exptruns('xpph4915',[17],230))
#exptlist.append(exptruns('xppc0115',[328,335],240))
#exptlist.append(exptruns('xpp02016',[225,272,300],250))
#exptlist.append(exptruns('xcs01116',[81,82,83,120],260))
#exptlist.append(exptruns('cxi06216',[22],270))
#exptlist.append(exptruns('amoi0216',[32,34],280))
#exptlist.append(exptruns('amoc0113',[217,219],290))
#exptlist.append(exptruns('diamcc14',[920,921,922],300))
#exptlist.append(exptruns('amol9416',[272],310))
#exptlist.append(exptruns('xppl4416',[283,284],320))
#exptlist.append(exptruns('sxr82112',[197],330))
#exptlist.append(exptruns('cxi12016',[24],30))
#exptlist.append(exptruns('amo06516',[10,15,19],340))
#exptlist.append(exptruns('amo01616',[125],350))
#exptlist.append(exptruns('amo01616',[20],360))
#exptlist.append(exptruns('cxilp7315',[21],370))
#exptlist.append(exptruns('cxilp9915',[162],380))
#exptlist.append(exptruns('amod3814',[85],390))
#exptlist.append(exptruns('sxri0215',[155],400))
#exptlist.append(exptruns('mfx11116',[691,694],410))
#exptlist.append(exptruns('sxrx24615',[22,23,24],420))
#exptlist.append(exptruns('mfx11116',[664,677],430))
#exptlist.append(exptruns('sxrx21715',[193],440))
#exptlist.append(exptruns('sxrx20915',[40,64],450))
#exptlist.append(exptruns('mec70013',[454],460))
#exptlist.append(exptruns('meco1416',[250,256],470))
#exptlist.append(exptruns('mecls3115',range(157,169),480)) #more than 10 runs!
#exptlist.append(exptruns('mecdaq115',[71,72],500))
#exptlist.append(exptruns('mecx24215',[72,121],510))
#exptlist.append(exptruns('sxrx21715',[191],520))
#exptlist.append(exptruns('detdaq17',[256],530))
#exptlist.append(exptruns('xcsx35617',[421],540))
#exptlist.append(exptruns('mfxx45919',list(range(9,19)),550))
#exptlist.append(exptruns('mfxx45919',list(range(80,86)),570))
#exptlist.append(exptruns('cxilw5019',list(range(248,251)),580))
#exptlist.append(exptruns('meclx9920',[634],590))  # cpo: mikhail did not use xpptut15_copy.py to populate run 590 I believe, so may be broken
#exptlist.append(exptruns('xppx53620',[74],600))
#exptlist.append(exptruns('cxilu9218',[12],610))
exptlist.append(exptruns('amox23616',[104,131,137],620))

rootdir = '/reg/d/psdm'
datadirs = ['xtc/index','xtc/smalldata','xtc']
outtopdir = os.path.join(rootdir,'xpp/xpptut15')
for e in exptlist:
    expt = e.expt
    inruns = e.inruns
    outruns_start = e.outruns_start
    hutch = expt[:3]
    outruns = range(outruns_start,outruns_start+len(inruns)+1)
    copyconstants(hutch,expt,inruns,outruns)
    for dd in datadirs:
        outfiles = []
        outdir = os.path.join(outtopdir,dd)
        for rin,rout in zip(inruns,outruns):
            infs = glob.glob(os.path.join(rootdir,hutch,expt,dd,'*r%4.4d*'%rin))
            if len(infs)==0:
                print '*** No input files found for exp=%s:run=%d'%(expt,rin),'in directory',dd
            for inf in infs:
                _,outf = os.path.split(inf)
                end = outf.split('-')
                outf = os.path.join(outdir,'e665-r'+ ('%4.4d'%rout) + '-' + end[2] + '-' + end[3])
                safecopy(inf,outf)
                if outf.endswith('.xtc'): fixRunNumber(outf)
