import numpy as np
import signal_manager as sm
import matplotlib.pyplot as plt
from network import Network
from keras.callbacks import ModelCheckpoint


class Trainer:
    def __init__(self, trader, nrof_epoch, batch_size, forward_look, backward_look,  nrof_bins):
        self.nrof_epoch = nrof_epoch
        self.batch_size = batch_size
        self.forward_look = forward_look
        self.backward_look = backward_look
        self.nrof_bins = nrof_bins
        self.trader = trader



    def train(self, data):
        available_windows = np.array(range(0, len(data) - self.forward_look - self.backward_look))
        np.random.shuffle(available_windows)
        choosen_windows = available_windows
        datax = [sm.exsax(sm.preprocess(data[window:window + self.backward_look]), self.nrof_bins) for window in
                 choosen_windows]
        datay = [sm.future_description(
            data[window + self.backward_look:window + self.backward_look + self.forward_look] - data[
                window + self.backward_look - 1]) for window in choosen_windows]
        np.savez("converted_data", datax=datax, datay=datay)
        for epoch in range(self.nrof_epoch):
            #datax = np.reshape(datax, (len(datax), 1, -1))
            self.trader.brain.fit(np.array(datax),np.array(datay),self.batch_size)
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


