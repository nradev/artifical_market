from math import exp, sqrt
from random import gauss

class Stock:
    def __init__(self, ticker, model, init_price=10, outstanding_shares=1000,
                 init_dividend=0.2, dividend_freq = 4, dividend_growth = 0.01, dividend_vol=0.2, div_noise_sig=0.1):
        self.ticker = ticker
        self.model = model
        self.price = init_price
        self.outstanding_shares = outstanding_shares
        self.init_dividend = init_dividend
        self.dividend = init_dividend
        self.dividend_freq = dividend_freq
        self.dividend_growth = dividend_growth
        self.dividend_vol = dividend_vol
        self.div_noise_sig = div_noise_sig

    def update_dividend(self):
        # Stochastic Dividend
        self.dividend *= exp((self.dividend_growth - 0.5*(self.dividend_vol**2))*(1/self.dividend_freq)
                             + self.dividend_vol*sqrt(1/self.dividend_freq)*gauss(0, self.div_noise_sig))

        # Mean Reverting Dividend
        # self.dividend = self.init_dividend + 0.95 * (self.dividend - self.init_dividend) \
        #                 + gauss(0, self.div_noise_sig*self.dividend*(1/self.dividend_freq))
        #                 # + gauss(0, self.dividend_vol*self.dividend*self.model.dt)
