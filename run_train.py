# -*- coding: utf-8 -*-

import numpy as np
import signal_manager as sm
from train import Trainer
from market_simulator import MarketSimulator
from trader import Trader
from network import Network
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, help="The folder in which the dataset is in")
    parser.add_argument("--capital", type=float, help="The capital which is available for trade when testing")
    parser.add_argument("--batch_size", type=int, help="The batch size used for train")
    parser.add_argument("--train_test_ratio", type=float, help="The folder in which the dataset used for validation and testing is in.")
    parser.add_argument("--nrof_epoch", type=int, help="The number of epoch planned to run")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    data = np.load(args.source)
    datax = data["datax"]
    datay = data["datay"]
    original_data = data["original"][100020+int(len(datax) * args.train_test_ratio):,1]

    settings = data["settings"].item(0)
    train_datax = data["datax"][0:int(len(datax) * args.train_test_ratio)]
    test_datax = data["datax"][int(len(datax) * args.train_test_ratio):]
    train_datay = data["datay"][0:int(len(datay) * args.train_test_ratio)]
    test_datay = data["datay"][int(len(datay) * args.train_test_ratio):]
    net = Network(input_size=settings["nrof_bins"] * 2)
    market_simulator = MarketSimulator(datax=test_datax,
                                       datay=test_datay,
                                       capital=args.capital,
                                       data_original=original_data,
                                       margin=0.0034,
                                       handicap=2)

    trader = Trader(create_indicator=lambda x: x,
                    brain=net,
                    backward_look=-1,
                    source=market_simulator,
                    ticks_between_actions=settings["look_forward"],
                    max_contract_time=settings["look_forward"])

    trainer = Trainer(trader=trader,
                      nrof_epoch=args.nrof_epoch,
                      batch_size=args.batch_size)

    trainer.train(datax=train_datax,
                  datay=train_datay)




