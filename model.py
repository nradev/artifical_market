import random
from environment.core.components import Agent, Model
from environment.core.scheduler import RandomActivation
from environment.order import Order, OrderBook
from environment.instruments import Stock
from agents.genetic import ForecastRule, RuleBook

class MarketAgent(Agent):
    def __init__(self, agent_id, model):
        super().__init__(agent_id, model)
        self.order_count = 0
        self.wealth = 1000
        self.stock_preference = random.random()
        self.stock_shares = 50
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth
        self.cash = self.wealth - self.stock_shares * self.model.stock.price
        self.rule_book = RuleBook(100)

    def step(self):
        self.recalculate_portfolio()
        self.rebalance()

    def recalculate_portfolio(self):
        self.wealth = self.cash + self.stock_shares * self.model.stock.price
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth

    def rebalance(self):
        share_demand = self.calculate_share_demand()
        trade_shares = share_demand - self.stock_shares
        # trade_price = self.calculate_trade_price()
        self.order_trade(trade_shares)

    def get_matched_rule_params(self):
        matched_rules = [rule for rule in self.rule_book.rules if rule.match_to_market(self.model)]
        best_rule = [rule for rule in matched_rules if rule.strength == max(rule.strength for rule in matched_rules)][0]
        return best_rule.a, best_rule.b, best_rule.sigma_sq

    def calculate_share_demand(self, risk_aversion=0.5):
        gamma = risk_aversion
        a, b, sigma_sq = self.get_matched_rule_params()
        exp_p_d = a * (self.model.stock.price + self.model.stock.dividend) + b
        share_demand = (exp_p_d - (1 + self.model.rf_rate) * self.model.stock.price) / (gamma * sigma_sq)
        return share_demand

    # def calculate_trade_price(self):
    #     return self.model.stock.price + (random.random() - 0.5)

    def order_trade(self, num_shares):
        if num_shares > 0:
            side = 'sell'
        else:
            side = 'buy'
            num_shares = -num_shares

        order = Order(self.agent_id, self.order_count, side, 'market', num_shares, self.model.current_step)
        self.model.order_book.add_order(order)

        if self.order_count < 50:
            self.order_count += 1
        else:
            self.order_count = 0


class MarketModel(Model):
    def __init__(self, N):
        super().__init__()
        self.running = True
        self.num_agents = N
        self.rf_rate = 0.01 #to be controlled by a regulator agent in the future
        self.current_step = 0
        ###self.matched_trades = []
        self.stock = Stock(ticker="STK", model=self, initial_price = 10, outstanding_shares = 1000,
                           equil_dividend = 0.2, dividend_vol = 0.2)
        self.schedule = RandomActivation(self)
        self.order_book = OrderBook(self)
        for i in range(self.num_agents):
            a = MarketAgent(i, self)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
        ###self.matched_trades = self.order_book.get_matched_trades()
        self.settle()
        self.current_step += 1
        self.stock.update_data(self.current_step, self.calculate_VWAP())

    def settle(self):
        sells = [x for x in self.orders if x.side == 'sell']
        buys = [x for x in self.orders if x.side == 'buy']

        agg_sells = min(sum([x.quantity for x in sells]), self.stock.outstanding_shares) # add Inventory
        agg_buys = min(sum([x.quantity for x in buys]), self.stock.outstanding_shares)

        available_sells = min(agg_sells, self.stock.outstanding_shares) #add Inventory
        available_buys = min(agg_buys, self.stock.outstanding_shares)

        buy_ratio = (min(agg_buys, available_sells) / agg_buys)
        sell_ratio = (min(agg_sells, available_buys) / agg_sells)

        self.stock.price = self.stock.price * (1 + eta * (agg_buys - agg_sells))

        for order in self.order_book:
            agent = self.schedule.agents[order.agent_id]
            if order.side == 'buy':
                trade_quantity = buy_ratio * order.quantity
                agent.stock_shares += trade_quantity
                agent.cash -= trade_quantity * self.stock.price
            if order.side == 'sell':
                trade_quantity = sell_ratio * order.quantity
                agent.stock_shares -= trade_quantity
                agent.cash += trade_quantity * self.stock.price

        self.order_book.clear()


    # def settle(self):
    #     for trade in self.matched_trades:
    #         agent = self.schedule.agents[trade.agent_id]
    #         agent.stock_shares += trade.quantity
    #         agent.cash -= trade.quantity * trade.price

    def calculate_VWAP(self):
        if not self.matched_trades: return self.stock.price
        trades = [x for x in self.matched_trades if x.quantity > 0]
        return sum(np.multiply([x.quantity for x in trades], [x.price for x in trades])) / sum(
            [x.quantity for x in trades])