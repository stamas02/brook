class MarketSimulator():
    def __init__(self, capital, data):
        self._data = data
        self._start_capital = capital
        self._capital = capital
        self._idx = 0
        self._contracts = []
        self.portfolio = [self._capital]
        self.margin = 0.0034

    def next(self):
        self._idx +=1

    def elapsed_minutes(self):
        return self._idx

    def reset(self):
        self._capital = self._start_capital
        self._contracts = []
        self.portfolio = [self._capital]

    def get_current_price(self):
        return self._data[self._idx]

    def cancel_contract(self, contract):

        current_price = self._data[self._idx]
        purchase_price = contract["price"]
        stake = contract["stake"]
        total_stake = stake/self.margin
        win = 0
        if contract["type"] == "buy":
            win = (float(total_stake)/purchase_price)*current_price
        elif contract["type"] == "short":
            win = (float(total_stake)/current_price)*purchase_price
        win = (win-total_stake)+stake
        self._capital += win-1

        self.portfolio.append(self._capital)

    def buy(self, stake):
        self._capital -= stake
        return {"type": "buy", "stake" :stake, "price" : self._data[self._idx]}

    def short(self,stake):
        self._capital -= stake
        return {"type": "short", "stake" :stake, "price" : self._data[self._idx]}

    def get_history(self, nrof_ticks):
        if nrof_ticks > self._idx:
            return None
        result =  self._data[self._idx-nrof_ticks+1:self._idx+1]
        if len(result)<nrof_ticks:
            return None
        return result

    def get_future(self, nrof_ticks):
        return self._data[self._idx:self._idx+nrof_ticks]
    def is_end(self):
        return len(self._data)<=self._idx

