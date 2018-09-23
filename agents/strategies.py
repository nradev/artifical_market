import random
from math import exp, sqrt
from environment.order import Order
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
        self.tolerance = 0.5 # profit slip tolerance
        self.neigh_exps = []
        self.interact_rate = self.model.glob_interact_rate

    def calc_exp_p_d(self):
        pass

    def calc_share_demand(self, stock=None): # stock argument to be used in multi stock simulation
        # self.recalc_exp_p_d()
        return (self.exp_p_d - (1 + self.model.rf_rate) * self.stock.price) / \
                       (self.agent.risk_aversion * self.sigma_sq)

    def calc_limit(self, stock=None):
        if self.model.settle_type == 'limit':
            limit_price = self.tolerance * self.exp_p_d \
                          + (1 - self.tolerance) * (1 + self.model.rf_rate)**self.model.dt * self.stock.price
        else:# self.model.settle_type == 'market':
            limit_price = None
        return limit_price

    def collect_neigh_exp(self):
        if self.model.current_step == 0: # drop condition if network not static
            self.agent.neighbors = [self.model.net.nodes[node]['agent_id'] for node
                                    in list(self.model.net.adj[self.agent.node])]
        self.neigh_exps = [self.model.schedule.agents[id].exp_p_d for id in self.agent.neighbors]

    def incorp_neighbour_exp(self):
        alpha = self.interact_rate
        neigh_average_exp = sum(self.neigh_exps) / len(self.neigh_exps)
        self.exp_p_d = (1 - alpha) * self.exp_p_d + alpha * neigh_average_exp
        return self.exp_p_d

class ZeroInformation(Strategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.strat_name = "zero_information"

    def calc_exp_p_d(self):
        self.exp_p_d = 0.9 * self.exp_p_d + 0.1 * (random.uniform(0.98, 1.02) * (self.stock.price
                                                                                 + self.stock.dividend))
        return self.exp_p_d


class Value(Strategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.strat_name = "value"
        self.div_noise_sig = random.uniform(0.05, 0.15)
        self.prev_dividend = self.stock.dividend

    def calc_exp_p_d(self):
        if self.model.current_step == 0 or self.prev_dividend != self.stock.dividend:
            # exp_d = self.stock.dividend * exp((self.stock.dividend_growth
            #                     - 0.5 * (self.stock.dividend_vol ** 2)) * (self.model.dt)
            #                     + self.stock.dividend_vol * sqrt(self.model.dt) * random.gauss(0, self.div_noise_sig))
            exp_d = self.stock.dividend * exp((self.stock.dividend_growth
                                - 0.5 * (self.stock.dividend_vol ** 2)) * (1/self.model.stock.dividend_freq)
                                + self.stock.dividend_vol * sqrt(1/self.model.stock.dividend_freq)
                                * random.gauss(0, self.div_noise_sig))
            self.prev_dividend = self.stock.dividend
            self.exp_p_d = exp_d / self.model.rf_rate + exp_d
        else: pass
        return self.exp_p_d


class Momentum(Strategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.strat_name = "momentum"
        self.prev_p_d = self.stock.price + self.stock.dividend

    def calc_exp_p_d(self):
        phi = random.uniform(0, 0.02)
        curr_p_d = self.stock.price + self.stock.dividend
        if curr_p_d == self.prev_p_d: self.exp_p_d = self.stock.price + self.stock.dividend
        elif curr_p_d > self.prev_p_d: self.exp_p_d = (self.stock.price + self.stock.dividend) * (1 + phi)
        elif curr_p_d < self.prev_p_d: self.exp_p_d = (self.stock.price + self.stock.dividend) * (1 - phi)
        self.prev_p_d = self.stock.price + self.stock.dividend
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