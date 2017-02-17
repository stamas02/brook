import numpy as np
import signal_manager as sm
import matplotlib.pyplot as plt
from network import Network
from keras.callbacks import ModelCheckpoint


class Trainer:
    def __init__(self, trader, nrof_epoch, batch_size):
        self.nrof_epoch = nrof_epoch
        self.batch_size = batch_size
        self.trader = trader



    def train(self, datax,datay):
        for epoch in range(self.nrof_epoch):
            #datax = np.reshape(datax, (len(datax), 1, -1))
            #datax = datax[:1000]
            #datay = datay[:1000]
            self.trader.brain.fit(x=np.array(datax,dtype=np.float32),
                                  y=np.array(datay),
                                  batch_size = self.batch_size,
                                  shuffle = True)
            self.trader.play()
            self.trader.reset()

    def visual_check(self, data, window):
        signal = sm.preprocess(data[window:window + self.backward_look])
        lines = sm.exsax(signal, self.nrof_bins)

        xs = range(len(signal))
        plt.plot(xs,signal)

        line_length = len(signal)/self.nrof_bins
        ys = np.zeros((self.nrof_bins,line_length))
        xs = np.zeros((self.nrof_bins,line_length))
        for x in range(len(signal)):
            d_index = x % line_length
            xs[int(x / line_length)][d_index]=x
            slope = lines[int(x / line_length)*2+1]
            mean = lines[int(x / line_length) * 2 ]
            ys[int(x / line_length)][d_index] = d_index*slope-slope*(line_length/2)+mean

        for x,y in zip(xs,ys):
            plt.plot(x, y, "-")
        plt.show()
        a = 3


