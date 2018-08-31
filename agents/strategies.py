import random
from math import exp, sqrt
from agents.genetic import ForecastRule, RuleBook

class Strategy:
    """ Base class for strategies. """
    def __init__(self, agent):
        self.strat_name = "Base"
        self.agent = agent
        self.model = agent.model
        self.stock = self.model.stock
        self.sigma_sq = self.stock.dividend_vol ** 2
        self.exp_p_d = self.stock.price + self.stock.dividend

    def recalc_exp_p_d(self):
        return self.exp_p_d

    def calc_share_demand(self, stock=None): # stock argument to be used in multi stock simulation
        self.recalc_exp_p_d()
        share_demand = (self.exp_p_d - (1 + self.model.rf_rate) * self.stock.price) / \
                       (self.agent.risk_aversion * self.sigma_sq)
        return share_demand


class ZeroInformation(Strategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.strat_name = "ZeroInformation"

    def recalc_exp_p_d(self):
        self.exp_p_d = 0.9 * self.exp_p_d + 0.1 * (random.uniform(0.98, 1.02) * (self.stock.price
                                                                                 + self.stock.dividend))
        return self.exp_p_d


class Value(Strategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.strat_name = "Value"
        self.div_noise_sig = random.uniform(0.05, 0.15)

    def recalc_exp_p_d(self):
        exp_d = self.stock.dividend * exp((self.stock.dividend_growth
                            - 0.5 * (self.stock.dividend_vol ** 2)) * (self.model.dt)
                            + self.stock.dividend_vol * sqrt(self.model.dt) * random.gauss(0, self.div_noise_sig))
        self.exp_p_d = exp_d / self.model.rf_rate + exp_d
        return self.exp_p_d


def get_matched_rule_params(agent, model):
    matched_rules = [rule for rule in agent.rule_book.rules if rule.match_to_market(model.stock)]
    best_rule = [rule for rule in matched_rules if rule.strength == max(rule.strength for rule in matched_rules)][0]
    return best_rule.a, best_rule.b, best_rule.sigma_sq

def genetic(agent, model):
    rule_book = RuleBook(100)
    price = model.stock.price
    dividend = model.stock.dividend
    rf_rate = model.rf_rate
    risk_aversion = model.glob_risk_aversion

    a, b, sigma_sq = get_matched_rule_params(agent, model)
    agent.exp_p_d = a * (price + dividend * model.dt) + b
    share_demand = (agent.exp_p_d - (1 + rf_rate) ** model.dt * price) / (risk_aversion * sigma_sq)
    return share_demand

# def zero_information(agent, model):  # (self, price, dividend, rf_rate, risk_aversion=0.5):
#     price = model.stock.price
#     dividend = model.stock.dividend
#     rf_rate = model.rf_rate
#     risk_aversion = model.glob_risk_aversion
#     dt = model.dt
#     sigma_sq = model.stock.dividend_vol ** 2
#     # agent.exp_p_d = 0.9 * agent.exp_p_d + 0.1 * random.uniform(0.98, 1.02) * price + dividend * dt
#     # share_demand = (agent.exp_p_d - ((1 + rf_rate) ** dt) * price) / (risk_aversion * sigma_sq * dt)
#     agent.exp_p_d = 0.9 * agent.exp_p_d + 0.1 * (random.uniform(0.98, 1.02) * (price + dividend))
#     share_demand = (agent.exp_p_d - (1 + rf_rate) * price) / (risk_aversion * sigma_sq)
#     return share_demand
#
# def value(agent, model):#(self, price, dividend, rf_rate, risk_aversion=0.5):
#     price = model.stock.price
#     dividend = model.stock.dividend
#     rf_rate = model.rf_rate
#     risk_aversion = model.glob_risk_aversion
#     dividend_growth = model.stock.dividend_growth
#     dividend_vol = model.stock.dividend_vol
#     dt = model.dt
#     sigma_sq = model.stock.dividend_vol ** 2
#     div_noise_sig = random.uniform(0.05, 0.15)
#     exp_d = dividend * exp((dividend_growth - 0.5*(dividend_vol**2))*(dt)
#                         + dividend_vol*sqrt(dt)*random.gauss(0, div_noise_sig))
#     agent.exp_p_d = exp_d / rf_rate + exp_d
#     share_demand = (agent.exp_p_d - (1 + rf_rate) * price) / (risk_aversion * sigma_sq)
#     return share_demand