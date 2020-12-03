import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks, peak_widths
import os 

from psana import DataSource

class EdgeFinderResult(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

class EdgeFinder(object):

    height = 0.25 # factor from max - used in finding peaks

    def __init__(self, kernel, good_image=None, bgs=None):
        self.kernel = kernel

    def __call__(self, image, background):
        # check if background exists 
        if background is None:
            background = np.zeros(image.shape, dtype=image.dtype)

        # do the match filter and normalize
        convolved = np.convolve(image-background, self.kernel)
        convolved /= np.max(convolved)
        # avoid convolution edge effects
        convolved = convolved[len(self.kernel):-len(self.kernel)]

        # get first peak and its fwhm
        first_peak = np.argmax(convolved)
        first_fwhms = peak_widths(convolved, [first_peak], rel_height=0.5)
        
        # find more peaks by looking at anything > 25% of the first peak amplitude
        height = self.height * convolved[first_peak]
        peaks, _  = find_peaks(convolved, height=height, distance=first_fwhms[0][0]*2)
        peaks_amp = convolved[peaks]
        sort_indices = np.flip(np.argsort(peaks_amp))
        peaks_sort = peaks[sort_indices]
        peaks_amp_sort = peaks_amp[sort_indices]
        results_half = peak_widths(convolved, peaks_sort, rel_height=0.5)
        
        # check if we have second peak
        amplitude_next = None
        if len(peaks_sort) > 1:
            amplitude_next = peaks_amp_sort[1]

        return EdgeFinderResult(edge=peaks_sort[0], \
                                amplitude=peaks_amp_sort[0], \
                                fwhm=first_fwhms[0][0], \
                                amplitude_next=amplitude_next, \
                                ref_amplitude=np.mean(background), \
                                convolved=convolved, \
                                results_half=results_half)

ds = DataSource(exp='tmoc00118', run=209)
myrun = next(ds.runs())
opal2 = myrun.Detector('tmoopal2')
#timing = myrun.Detector('timing')
kernel = np.array(16*[-1]+16*[1]) # a derivative kernel
edge_finder = EdgeFinder(kernel)
background = None
myroi = np.s_[250:750,:]
plot = True

for nevt,evt in enumerate(myrun.events()):
    if nevt==0: continue
    image = opal2.raw.image(evt)
    #codes = timing.raw.eventcodes(evt)
    # if codes is None: continue
    if image is None: continue

    #if 162 in codes: # background shot? subtract, for example, etalon effect
    #    if background is None:
    #        background = image[myroi]
    #    else:
    #        background = 0.9*background+0.1*image[myroi]
    #    continue

    # daq "ttfex" results: see https://confluence.slac.stanford.edu/display/PSDM/TimeTool
    # ampl, amplnxt, fltpos, fltpos_ps, fltposfwhm, proj_ref, proj_sig, refampl
    # only valid if it's not a background shot (e.g. BYKIK)
    daq_edge = opal2.ttfex.fltpos(evt)

    # take ROI and project
    image = np.sum(image[myroi],axis=1)
    result = edge_finder(image, background)

    if plot:
        plt.plot(image/np.max(image), label="signal")
        plt.plot(result.convolved, label="convolution result")
        plt.plot(result.edge, result.amplitude, "x")
        plt.hlines(*result.results_half[1:], color="C2")
        # there is also a result.amplitude_next, but can be None
        plt.title(f'edge_pos={result.edge:d} fwhm={result.fwhm:.2f} ampl={result.amplitude:.2f} ref_ampl={result.ref_amplitude:.2f}')
        plt.legend()
        plt.xlabel('pixel number')
        plt.ylabel('normalized signal')
        plt.show()
