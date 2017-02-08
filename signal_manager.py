import numpy as np
from scipy import stats
import math
def exsax(signal,nrof_bin):
    data = []
    assert len(signal) % nrof_bin == 0, "signal length must be divisable by the bin number"
    length = len(signal)/nrof_bin
    for b in range(nrof_bin):
        s = signal[b*length:(b+1)*length]
        mean = np.mean(s)
        slope, _, _, _, _ = stats.linregress(range(len(s)), s)
        if math.isnan(mean):
            d = 7
        if math.isnan(slope):
            d = 7
        data.append(mean)
        data.append(slope)
    return np.array(data)


def preprocess(signal):
    original = np.array(signal)
    signal = stats.mstats.zscore(signal)
    if math.isnan(signal[0]):
        return np.zeros_like(signal)
    return signal

def future_description(signal):
    signal = np.insert(signal,0,0)
    max_mean = np.mean(signal[signal>=0])
    min_mean = np.mean(signal[signal<=0])

    return max_mean, min_mean, np.mean(signal), np.std(signal)
