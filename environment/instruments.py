from math import exp, sqrt
from random import gauss
from scipy.stats import tstd, skew, kurtosis

class Stock:
    def __init__(self, ticker, model, init_price=10, outstanding_shares=1000,
                 init_dividend=0.2, dividend_freq = 4, dividend_growth = 0.01, dividend_vol=0.2, div_noise_sig=0.1):
        self.ticker = ticker
        self.model = model
        self._price = init_price
        self.outstanding_shares = outstanding_shares
        self.init_dividend = init_dividend
        self.dividend = init_dividend
        self.dividend_freq = dividend_freq
        self.dividend_growth = dividend_growth
        self.dividend_vol = dividend_vol
        self.div_noise_sig = div_noise_sig

        self.last_return = None
        self.vol = None
        self.skew= None
        self.kurt = None

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, new_price):
        self.last_return = new_price / self._price - 1
        self.vol, self.skew, self.kurt = self.calc_moments()
        self._price = new_price

    def update_dividend(self):
        # Stochastic Dividend
        self.dividend *= exp((self.dividend_growth - 0.5*(self.dividend_vol**2))*(1/self.dividend_freq)
                             + self.dividend_vol*sqrt(1/self.dividend_freq)*gauss(0, self.div_noise_sig))

        # Mean Reverting Dividend
        # self.dividend = self.init_dividend + 0.95 * (self.dividend - self.init_dividend) \
        #                 + gauss(0, self.div_noise_sig*self.dividend*(1/self.dividend_freq))
        #                 # + gauss(0, self.dividend_vol*self.dividend*self.model.dt)

    def calc_last_return(self):
        pass

    def calc_moments(self, periods=252):
        if self.model.current_step - 1 < periods:
            return None, None, None
        else:
            rets = self.model.datacollector.model_vars["Return"][-periods-1:]
            rets.append(self.last_return)
            return tstd(rets), skew(rets), kurtosis(rets)
