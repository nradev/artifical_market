from math import exp, sqrt

class Stock:
    def __init__(self, ticker, model, init_price=10, outstanding_shares=1000,
                 init_dividend=0.2, dividend_freq = 4, dividend_growth = 0.01, dividend_vol=0.2):
        self.ticker = ticker
        self.model = model
        self.price = init_price
        self.outstanding_shares = outstanding_shares
        self.price_hist = {0: init_price}
        self.market_cap = self.price * outstanding_shares
        self.init_dividend = init_dividend
        self.dividend_freq = dividend_freq
        self.dividend_growth = dividend_growth
        self.dividend_vol = dividend_vol
        self.dividend = init_dividend
        self.price_MA_5 = init_price
        self.price_MA_10 = init_price
        self.price_MA_50 = init_price
        self.price_MA_100 = init_price
        self.price_MA_5_hist = {0: init_price}
        self.price_MA_10_hist = {0: init_price}
        self.price_MA_50_hist = {0: init_price}
        self.price_MA_100_hist = {0: init_price}
        self.PID_ratio = (self.price * self.model.rf_rate) / self.dividend
        # self.rule_string = ""
        # for v in [0.25, 0.50, 0.75, 0.875, 1.0, 1.125]:
        #     self.rule_string += "1" if self.PID_ratio > v else "0"
        # self.rule_string += "1" if self.price_MA_5 < model.stock.price else "0"
        # self.rule_string += "1" if self.price_MA_10 < model.stock.price else "0"
        # self.rule_string += "1" if self.price_MA_50 < model.stock.price else "0"
        # self.rule_string += "1" if self.price_MA_100 < model.stock.price else "0"
        # self.rule_string += "10"

    def update_data(self, time_step, new_price):
        self.price_hist[time_step] = new_price
        self.price = new_price
        self.market_cap = self.price * self.outstanding_shares
        self.price_MA_5 = self.calculate_MA(5, time_step)
        self.price_MA_10 = self.calculate_MA(10, time_step)
        self.price_MA_50 = self.calculate_MA(50, time_step)
        self.price_MA_100 = self.calculate_MA(100, time_step)
        self.price_MA_5_hist[time_step] = self.price_MA_5
        self.price_MA_10_hist[time_step] = self.price_MA_10
        self.price_MA_50_hist[time_step] = self.price_MA_50
        self.price_MA_100_hist[time_step] = self.price_MA_100
        self.update_rule_string()

    def calculate_MA(self, periods, time_step):
        if periods < time_step - 1:
            return sum([v for k, v in self.price_hist.items()][-periods:]) / periods
        else:
            return sum([v for k, v in self.price_hist.items()]) / (time_step + 1)

    def update_dividend(self):
        from random import gauss
        # Stochastic Dividend
        # self.dividend *= exp((self.dividend_growth - 0.5*(self.dividend_vol**2))*(1/self.dividend_freq)
        #                      + self.dividend_vol*sqrt(1/self.dividend_freq)*gauss(0, 3))

        # Mean Reverting Dividend
        self.dividend = self.init_dividend + 0.95 * (self.dividend - self.init_dividend) \
                        + gauss(0, self.dividend_vol*self.dividend*self.model.dt)
        self.PID_ratio = (self.price * self.model.rf_rate) / self.dividend

    def update_rule_string(self):
        new_string = ""
        for v in [0.25, 0.50, 0.75, 0.875, 1.0, 1.125]:
            new_string += "1" if self.PID_ratio > v else "0"
        new_string += "1" if self.price_MA_5 < self.model.stock.price else "0"
        new_string += "1" if self.price_MA_10 < self.model.stock.price else "0"
        new_string += "1" if self.price_MA_50 < self.model.stock.price else "0"
        new_string += "1" if self.price_MA_100 < self.model.stock.price else "0"
        new_string += "10"
        self.rule_string = new_string

        # lat = [v for k, v in self.price_hist.items()]
        # den = (self.model.current_step + 1)
        # if periods < self.model.current_step:
        #     lat = lat[-periods:]
        #     den = periods
        # return sum(lat) / den