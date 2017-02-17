class MarketSimulator():
    def __init__(self, capital, datax, datay, data_original, margin, handicap):
        self._datax = datax
        self._datay = datay
        self._data_original = data_original
        self._start_capital = capital
        self._capital = capital
        self._idx = 0
        self._contracts = []
        self.portfolio = [self._capital]
        self.margin = margin#0.0034
        self.handicap = handicap

    def next(self):
        self._idx +=1

    def elapsed_minutes(self):
        return self._idx

    def reset(self):
        self._capital = self._start_capital
        self._contracts = []
        self.portfolio = [self._capital]

    def get_current_price(self):
        return self._data_original[self._idx]

    def cancel(self, contract):

        current_price = self.get_current_price()
        purchase_price = contract["price"]
        stake = contract["stake"]
        total_stake = stake/self.margin
        win = 0
        if contract["type"] == "buy":
            win = (float(total_stake)/purchase_price)*current_price
        elif contract["type"] == "short":
            win = (float(total_stake)/current_price)*purchase_price
        win = (win-total_stake)+stake
        self._capital += win-self.handicap

        self.portfolio.append(self._capital)

    def buy(self, stake):
        self._capital -= stake
        return {"type": "buy", "stake" :stake, "price" : self.get_current_price()}

    def short(self,stake):
        self._capital -= stake
        return {"type": "short", "stake" :stake, "price" : self.get_current_price()}

    def get_history(self, last_n):
        return self._datax[self._idx]

    def get_future(self):
        return self._datay[self._idx]

    def is_end(self):
        return len(self._datax)<=self._idx

