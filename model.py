import random
from environment.core.components import Agent, Model
from environment.core.scheduler import RandomActivation
from environment.order import Order, OrderBook
from environment.instruments import Stock
from agents.strategies import zero_information, genetic
from agents.genetic import RuleBook

class MarketAgent(Agent):
    def __init__(self, agent_id, model, init_shares, init_wealth, strategy = 'zero_information'):
        super().__init__(agent_id, model)
        self.agent_id = agent_id
        self.order_count = 0
        self.wealth = init_wealth
        self.stock_shares = init_shares
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth
        self.cash = self.wealth - self.stock_shares * self.model.stock.price
        if strategy == 'zero_information':
            self.calculate_share_demand = zero_information
        elif strategy == 'genetic':
            self.calculate_share_demand = genetic
            self.rule_book = RuleBook(100)

    def step(self):
        self.recalculate_portfolio()
        self.rebalance()

    def recalculate_portfolio(self):
        self.wealth = self.cash + self.stock_shares * self.model.stock.price
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth

    def rebalance(self):
        share_demand = self.calculate_share_demand(self, self.model) #self.model.stock.price, self.model.stock.dividend, self.model.rf_rate, self.model.glob_risk_aversion)
        #if self.agent_id == 5: print(share_demand)
        trade_shares = share_demand - self.stock_shares
        # trade_price = self.calculate_trade_price()
        if trade_shares > 0:
            self.order_trade(min(trade_shares, self.model.max_long*self.model.stock.outstanding_shares))
        if trade_shares < 0:
            self.order_trade(max(trade_shares, -self.model.max_short*self.model.stock.outstanding_shares))

    def order_trade(self, num_shares):
        if num_shares > 0:
            side = 'buy'
        else:
            side = 'sell'
            num_shares = -num_shares

        order = Order(self.agent_id, self.order_count, side, 'market', num_shares, self.model.current_step)
        self.model.order_book.add_order(order)

        if self.order_count < 50:
            self.order_count += 1
        else:
            self.order_count = 0


class MarketModel(Model):
    def __init__(self, n_agents, init_rf = 0.02, n_shares = 1000, glob_risk_aversion = 0.5, init_price = 50, equil_dividend = 0.2,
                 dividend_vol = 0.2, price_adj_speed = 0.1, max_short = 0.0001, max_long = 0.02):
        super().__init__()
        self.running = True
        self.n_agents = n_agents
        self.glob_risk_aversion = glob_risk_aversion
        self.rf_rate = init_rf #to be controlled by a regulator agent in the future
        self.eta = price_adj_speed
        self.max_short = max_short
        self.max_long = max_long
        self.current_step = 0
        ###self.matched_trades = []
        self.stock = Stock(ticker="STK", model=self, initial_price = init_price, outstanding_shares = n_shares,
                           equil_dividend = equil_dividend, dividend_vol = dividend_vol)
        self.schedule = RandomActivation(self)
        self.order_book = OrderBook()
        for i in range(self.n_agents):
            a = MarketAgent(i, self, n_shares/n_agents, 1000, 'zero_information')
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
        ###self.matched_trades = self.order_book.get_matched_trades()
        self.settle()
        self.current_step += 1
        self.stock.update_data(self.current_step, self.stock.price)

    def settle(self):
        sells = [x for x in self.order_book.orders if x.side == 'sell']
        buys = [x for x in self.order_book.orders if x.side == 'buy']

        if not (sells and buys):
            return

        agg_sells = sum([x.quantity for x in sells])
        agg_buys = sum([x.quantity for x in buys])

        available_sells = min(agg_sells, self.stock.outstanding_shares) #add Inventory
        available_buys = min(agg_buys, self.stock.outstanding_shares)

        buy_ratio = (min(agg_buys, available_sells) / agg_buys)
        sell_ratio = (min(agg_sells, available_buys) / agg_sells)

        #print(agg_buys, agg_sells)
        self.stock.price = self.stock.price * (1 + self.eta * (agg_buys - agg_sells)) # find a better price mechanism

        for order in self.order_book.orders:
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
    #
    # def calculate_VWAP(self):
    #     if not self.matched_trades: return self.stock.price
    #     trades = [x for x in self.matched_trades if x.quantity > 0]
    #     return sum(np.multiply([x.quantity for x in trades], [x.price for x in trades])) / sum(
    #         [x.quantity for x in trades])