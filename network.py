from keras.models import Sequential
from keras.layers import Dense, Activation
import keras as kr
import numpy as np
from keras.callbacks import ModelCheckpoint

class Network:
    def __init__(self, input_size):
        self.input_size = input_size
        self._model = Sequential()
        self._model.add(Dense(100, input_dim=input_size))
        self._model.add(Dense(100))
        self._model.add(Dense(4))
        sgd = kr.optimizers.adagrad(lr=.1)
        self._model.compile(optimizer=sgd,
                      loss='mean_squared_error',
                      metrics=['accuracy'],)
        self._epoch = 0


    def fit(self, x,y,batch_size, shuffle):
        filename = "checkpoints/checkpoint-" + str(self._epoch) + "-{loss:.2f}.hdf5"
        self._epoch += 1
        return self._model.fit(x,y,batch_size,1,
                               callbacks=[ModelCheckpoint(filename)],
                               shuffle=shuffle)



    def predict(self, x):
        return self._model.predict(np.array([x]),batch_size=1)[0]