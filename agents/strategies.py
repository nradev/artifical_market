import random
from agents.genetic import ForecastRule, RuleBook

def zero_information(agent, model):#(self, price, dividend, rf_rate, risk_aversion=0.5):
    price = model.stock.price
    dividend = model.stock.dividend
    rf_rate = model.rf_rate
    risk_aversion = model.glob_risk_aversion
    dt = model.dt
    sigma_sq = model.stock.dividend_vol ** 2
    # agent.exp_p_d = 0.9 * agent.exp_p_d + 0.1 * random.uniform(0.98, 1.02) * price + dividend * dt
    # share_demand = (agent.exp_p_d - ((1 + rf_rate) ** dt) * price) / (risk_aversion * sigma_sq * dt)
    agent.exp_p_d = 0.9 * agent.exp_p_d + 0.1 * (random.uniform(0.98, 1.02) * (price + dividend))
    share_demand = (agent.exp_p_d - (1 + rf_rate) * price) / (risk_aversion * sigma_sq)
    return share_demand

def get_matched_rule_params(agent, model):
    matched_rules = [rule for rule in agent.rule_book.rules if rule.match_to_market(model.stock)]
    best_rule = [rule for rule in matched_rules if rule.strength == max(rule.strength for rule in matched_rules)][0]
    return best_rule.a, best_rule.b, best_rule.sigma_sq

def genetic(agent, model):
    price = model.stock.price
    dividend = model.stock.dividend
    rf_rate = model.rf_rate
    risk_aversion = model.glob_risk_aversion

    a, b, sigma_sq = get_matched_rule_params(agent, model)
    agent.exp_p_d = a * (price + dividend * model.dt) + b
    share_demand = (agent.exp_p_d - (1 + rf_rate) ** model.dt * price) / (risk_aversion * sigma_sq)
    return share_demand