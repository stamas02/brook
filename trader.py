import signal_manager as sm
import math
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import cv2

class Trader:
    def __init__(self, brain,backward_look,nrof_bins, source, ticks_between_actions, max_contract_time):
        self.brain = brain
        self._source = source
        self._ticks_between_actions = ticks_between_actions
        self._max_contract_time = max_contract_time
        self._backward_look = backward_look
        self._nrof_bins = nrof_bins
        self.stake = 100
        self._contracts = []


    def play(self):
        last_action = self._ticks_between_actions
        while not self._source.is_end():
            history = self._source.get_history(self._backward_look)
            if history is None:
                self._source.next()
                continue

            signal = sm.exsax(sm.preprocess(history),self._nrof_bins)
            #future  = np.array(self._source.get_future(15))
            #future -= future[0]
            #maxx, minn, mean, std = sm.future_description(future)
            maxx, minn, mean, std = self.brain.predict(signal)
            if last_action > self._ticks_between_actions:
                if self.make_contract(maxx, minn, mean, std):
                    last_action = -1
            last_action+= 1
            self.sell_contract(self._source.get_current_price()+maxx, self._source.get_current_price()+minn)
        self.save_portfolio()


    def reset(self):
        self._contracts = []
        self._source.reset()

    def make_contract(self, maxx, minn, mean, std):
        made_action = False
        current_price = self._source.get_current_price()
        buy_profit = self.calculate_profit(current_price,current_price+maxx,self._source.margin,self.stake,"buy")
        short_profit = self.calculate_profit(current_price,current_price+minn,self._source.margin,self.stake,"short")
        if buy_profit > short_profit and buy_profit > 1:
            _contract = self._source.buy(self.stake)
            contract = {"contract: " : _contract}
            contract["trader_data"] = {"life_time": 0,
                                       "risk": 0,
                                       "estimated_maximum": current_price+maxx,
                                       "estimated_minimum": current_price+minn, "estimated_mean": mean,
                                       "estiamted_std": std,
                                       "type" : "Buy"}
            self._contracts.append(contract)
            made_action = True
        elif buy_profit < short_profit and short_profit > 1:
            _contract = self._source.short(self.stake)
            contract = {"contract: " : _contract}
            contract["trader_data"] = {"life_time": 0,
                                       "risk": 0,
                                       "estimated_maximum": current_price+maxx,
                                       "estimated_minimum": current_price+minn, "estimated_mean": mean,
                                       "estiamted_std": std,
                                       "type": "Short"}
            self._contracts.append(contract)
            made_action = True

        return made_action

    def save_portfolio(self):
        fig = plt.figure(figsize=(50, 50), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        fig.hold(True)
        ax.plot(range(0,len(self._source.portfolio)), self._source.portfolio)
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()
        image = np.fromstring(fig.canvas.tostring_rgb(), dtype='uint8')
        image.shape = (h, w, 3)
        filename = str(self.brain._epoch)+"_.jpg"
        cv2.imwrite(filename, image)


    def sell_contract(self, current_estimated_maximum, current_estimated_minimum):
            for contract in self._contracts:
                if contract["trader_data"]["life_time"] == -1:
                    continue
                contract["trader_data"]["life_time"] += 1
                current_price = self._source.get_current_price()
                if  contract["trader_data"]["life_time"] > self._max_contract_time:
                    self._source.cancel(contract["contract"])
                    contract["trader_data"]["life_time"] = -1
                if  contract["trader_data"]["risk"] > 2:
                    self._source.cancel(contract)
                    contract["trader_data"]["life_time"] = -1
                if  contract["trader_data"]["type"] == "buy":
                    if current_price > contract["trader_data"]["estimated_maximum"]:
                        self._source.cancel(contract["contract"])
                        contract["trader_data"]["life_time"] = -1
                    if contract["trader_data"]["estimated_maximum"] >current_estimated_maximum:
                        contract["trader_data"]["risk"] += 1
                    elif contract["trader_data"]["risk"] > 0:
                        contract["trader_data"]["risk"] -= 1
                if  contract["trader_data"]["type"] == "short":
                    if current_price < contract["trader_data"]["estimated_minimum"]:
                        self._source.cancel(contract["contract"])
                        contract["trader_data"]["life_time"] = -1
                    if contract["trader_data"]["estimated_minimum"] <current_estimated_minimum:
                        contract["trader_data"]["risk"] += 1
                    elif contract["trader_data"]["risk"] > 0:
                        contract["trader_data"]["risk"] -= 1
            self._source.next()

    def calculate_profit(self, past_price, current_price, margin, stake, contract_type ):

        total_stake = stake / margin
        win = 0
        if contract_type == "buy":
            win = (float(total_stake) / past_price) * current_price
        elif contract_type == "short":
            win = (float(total_stake) / current_price) * past_price
        win = (win - total_stake)
        return win
