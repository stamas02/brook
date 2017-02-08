# -*- coding: utf-8 -*-

import numpy as np
import signal_manager as sm
from train import Trainer
from market_simulator import MarketSimulator
from trader import Trader
from network import Network



CAPITAL = 100
BACKWARD_LOOK = 20
FORWARF_LOOK = 15
NROF_BINS = 5
TICKS_BETWEEN_ACTIONS = 15
MAX_CONTRACT_TIME = 15
BATCH_SIZE = 90
NROF_EOPCH = 50
TRAIN_TEST_RATIO = 0.95
#DATA_SOURCE = '/media/tamas/Sör2/CurrencyData/data.npz'
DATA_SOURCE = '~/Datasets/Currency/data.npz'




data = np.load(DATA_SOURCE)
data = data['AUDCAD.npy']
data = data[100000:, 1]
train_data = data[0:int(len(data)*TRAIN_TEST_RATIO)]
test_data = data[int(len(data)*TRAIN_TEST_RATIO):]


#train_data = data[0:30000]
#test_data = data[-10000:]


net = Network(input_size=5*2)




market_simulator = MarketSimulator(capital=CAPITAL,
                                   data=test_data)

trader = Trader(brain=net,
                backward_look=BACKWARD_LOOK,
                nrof_bins=NROF_BINS,
                source=market_simulator,
                ticks_between_actions=TICKS_BETWEEN_ACTIONS,
                max_contract_time=MAX_CONTRACT_TIME)

trainer = Trainer(trader = trader,
                  nrof_epoch = NROF_EOPCH,
                  batch_size = BATCH_SIZE,
                  forward_look = FORWARF_LOOK,
                  backward_look = BACKWARD_LOOK,
                  nrof_bins = NROF_BINS)


trainer.train(train_data)


