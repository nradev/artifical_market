import random
import numpy as np
import networkx as nx
from mesa import Agent, Model
from mesa.time import StagedActivation
from environment.core.datacollection import ModDataCollector
from environment.order import Order, OrderBook, Trade
from environment.instruments import Stock
from agents.strategies import ZeroInformation, Value, Momentum
import matplotlib.pyplot as plt

class MarketAgent(Agent):
    def __init__(self, agent_id, model, init_shares, init_wealth, risk_aversion,
                 strategy='zero_information', particip_rate=1):
        super().__init__(agent_id, model)
        self.agent_id = agent_id
        self.order_count = 0
        self.wealth = init_wealth
        self.stock_shares = init_shares
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth
        self.cash = self.wealth - self.stock_shares * self.model.stock.price
        self.risk_aversion = risk_aversion
        self.exp_p_d = None
        self.share_demand = None
        self.limit = None
        self.target_shares = None
        self.trade_shares = None
        self.particip_rate =  particip_rate
        if strategy == 'zero_information':
            self.strategy = ZeroInformation(self)
        elif strategy == 'value':
            self.strategy = Value(self)
        elif strategy == 'momentum':
            self.strategy = Momentum(self)
        self.node = None
        self.neighbors = []

    def stage1(self):
        self.recalculate_portfolio()
        self.exp_p_d = self.strategy.calc_exp_p_d()

    def stage2(self):
        self.strategy.collect_neigh_exp()

    def stage3(self):
        self.exp_p_d = self.strategy.incorp_neighbour_exp()
        self.share_demand = self.strategy.calc_share_demand()
        self.limit = self.strategy.calc_limit()
        if random.random() < self.particip_rate:
            self.rebalance()

    def recalculate_portfolio(self):
        self.wealth = self.cash + self.stock_shares * self.model.stock.price
        self.stock_weight = (self.stock_shares * self.model.stock.price) / self.wealth

    def rebalance(self):
        # self.share_demand, self.limit = self.strategy.calc_order()
        self.target_shares = self.share_demand - self.stock_shares
        max_leverage = 0.2
        trade_for_max_w = ((self.wealth * (1 + max_leverage)) / self.model.stock.price - self.stock_shares)
        trade_for_min_w = -((self.wealth * max_leverage) / self.model.stock.price + self.stock_shares)
        if self.target_shares > 0:
            self.trade_shares = min(self.target_shares, self.model.max_long*self.model.stock.outstanding_shares
                                    - self.stock_shares, trade_for_max_w)
        elif self.target_shares < 0:
            self.trade_shares = max(self.target_shares, -(self.model.max_short*self.model.stock.outstanding_shares
                                    + self.stock_shares), trade_for_min_w)
        else: return
        self.order_trade(self.trade_shares, self.limit)

    def order_trade(self, num_shares, limit=None):
        if num_shares > 0:
            side = 'buy'
        else:
            side = 'sell'
            num_shares = -num_shares
        if limit == None:
            order = Order(self.agent_id, self.order_count, side, num_shares, self.model.current_step, 'market')
        else:
            order = Order(self.agent_id, self.order_count, side, num_shares, self.model.current_step, 'limit', limit)
        self.model.order_book.add_order(order)
        if self.order_count < 50:
            self.order_count += 1
        else:
            self.order_count = 0


class MarketModel(Model):
    def __init__(self, n_agents, population_composition={'zero_information': 1}, settle_type='limit', dt=1/252,
                 init_rf=0.02, n_shares=1000, init_agent_wealth=1000, glob_risk_aversion=0.5, glob_interact_rate=0.25,
                 agent_particip_rate=1, init_price=50, init_dividend=5, dividend_freq=4, dividend_growth=0.01,
                 dividend_vol=0.2, div_noise_sig=0.1, price_adj_speed=0.1, max_short=0.0001, max_long=0.02):
        super().__init__()
        self.running = True
        self.n_agents = n_agents
        self.population_composition = population_composition
        self.glob_risk_aversion = glob_risk_aversion
        self.glob_interact_rate = glob_interact_rate
        self.rf_rate = init_rf #to be controlled by a regulator agent in the future
        self.eta = price_adj_speed
        self.max_short = max_short
        self.max_long = max_long
        self.current_step = 0
        self.dt = dt
        self.stock = Stock(ticker="STK", model=self, init_price = init_price, outstanding_shares = n_shares,
                           init_dividend = init_dividend, dividend_freq = dividend_freq,
                           dividend_growth = dividend_growth, dividend_vol = dividend_vol,
                           div_noise_sig=div_noise_sig)
        self.schedule = StagedActivation(self, ['stage1', 'stage2', 'stage3'])
        self.order_book = OrderBook()
        self.settle_type = settle_type
        agent_id = 0
        if sum([population_composition[key] for key in population_composition]) - 1.0 > 1e-06:
            raise NameError('population_compositions elements must sum up to 1')
        for key in population_composition:
            for i in range(int(population_composition[key] * self.n_agents)):
                init_shares = n_shares / n_agents
                a = MarketAgent(agent_id, self, init_shares, init_agent_wealth, glob_risk_aversion,
                                key, agent_particip_rate)
                self.schedule.add(a)
                agent_id += 1
        self.global_wealth = sum([agent.wealth for agent in self.schedule.agents])
        self.agg_sells = 0
        self.agg_buys = 0
        self.available_sells = 0
        self.available_buys = 0
        self.buy_ratio = 0
        self.sell_ratio = 0
        self.matched_trades = []
        self.datacollector = ModDataCollector(
            model_reporters={"Global Wealth": "global_wealth", "Price": "stock.price", "Dividend": "stock.dividend",
                             "Agg Sells": "agg_sells", "Agg Buys": "agg_buys", "Av Sells": "available_sells",
                             "Av Buys": "available_buys", "Buy Ratio": "buy_ratio", "Sell Ratio": "sell_ratio",
                             "Matched Trades": "matched_trades"},
            agent_reporters={"Wealth": "wealth", "Cash": "cash", "Stock Weight": "stock_weight",
                             "Stock Shares": "stock_shares", "Demand": "share_demand",
                             "Target Trade": "target_shares", "Actual Trade": "trade_shares",
                             "Price Expectation": "strategy.exp_p_d"})
        self.net = self.generate_net()
        # plt.plot()
        # nx.draw_kamada_kawai(self.net)
        # plt.show()

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.settle()
        self.current_step += 1
        for agent in self.schedule.agents:
            agent.cash *= (1 + self.rf_rate) ** self.dt
        if self.current_step % ((self.dt ** -1)/self.stock.dividend_freq) == 0:
            self.stock.update_dividend()
            for agent in self.schedule.agents:
                agent.cash += (self.stock.dividend/self.stock.dividend_freq) * agent.stock_shares
        self.global_wealth = sum([agent.wealth for agent in self.schedule.agents])

    def settle(self):
        if self.settle_type == 'limit':
            self.matched_trades = self.order_book.get_matched_trades()
            self.order_book.clear()
            for trade in self.matched_trades:
                buy_agent = self.schedule.agents[trade.buy_agent]
                sell_agent = self.schedule.agents[trade.sell_agent]
                buy_agent.stock_shares += trade.quantity
                buy_agent.cash -= trade.quantity * trade.price
                sell_agent.stock_shares -= trade.quantity
                sell_agent.cash += trade.quantity * trade.price
            self.stock.price = self.calculate_VWAP()
        elif self.settle_type == 'market':
            sells = [x for x in self.order_book.orders if x.side == 'sell']
            buys = [x for x in self.order_book.orders if x.side == 'buy']

            self.agg_sells = sum([x.quantity for x in sells])
            self.agg_buys = sum([x.quantity for x in buys])

            if (self.agg_sells==0 or self.agg_buys==0):
                return

            self.available_sells = min(self.agg_sells, self.stock.outstanding_shares) #add Inventory
            self.available_buys = min(self.agg_buys, self.stock.outstanding_shares)

            self.buy_ratio = (min(self.agg_buys, self.available_sells) / self.agg_buys)
            self.sell_ratio = (min(self.agg_sells, self.available_buys) / self.agg_sells)

            self.stock.price = self.stock.price * (1 + self.eta * (self.agg_buys - self.agg_sells)) # find a better price mechanism
            # rho = 0.95
            # f = rho / (1 + self.rf_rate - rho)
            # g = (1/self.rf_rate) * (1 + f) * (self.stock.init_dividend - self.glob_risk_aversion
            #                      * (self.stock.div_noise_sig**2) * (1000/self.n_agents))
            # self.stock.price = f * self.stock.dividend + g
            for order in self.order_book.orders:
                ### need to prelist if using RandomScheduler
                agent = self.schedule.agents[order.agent_id]
                if order.side == 'buy':
                    trade_quantity = self.buy_ratio * order.quantity
                    agent.stock_shares += trade_quantity
                    agent.cash -= trade_quantity * self.stock.price
                if order.side == 'sell':
                    trade_quantity = self.sell_ratio * order.quantity
                    agent.stock_shares -= trade_quantity
                    agent.cash += trade_quantity * self.stock.price
            self.order_book.clear()

    def calculate_VWAP(self):
        trades = [x for x in self.matched_trades if x.quantity > 0]
        volume = sum([x.quantity for x in trades])
        if volume <= 0: return self.stock.price
        return sum(np.multiply([x.quantity for x in trades], [x.price for x in trades])) / volume

    def generate_net(self):
        net = nx.scale_free_graph(self.n_agents, alpha=0.41, beta=0.25, gamma=0.34)
        net = nx.to_undirected(net)
        nodes = list(net.nodes)
        random.shuffle(nodes)
        for agent, node in zip(self.schedule.agents, nodes):
            agent.node = node
            net.nodes[node]['agent_id'] = agent.agent_id
        return net