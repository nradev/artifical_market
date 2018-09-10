class Order:
    def __init__(self, agent_id, order_id, side, quantity, time, order_type, limit_price=None):
        self.order_id = order_id
        self.agent_id = agent_id
        self.side = side
        self.quantity = quantity
        self.time = time
        self.order_type = order_type
        self.limit_price = limit_price


class OrderBook:
    def __init__(self):
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def clear(self):
        self.orders = []


    # def remove_order(self, agent_id, order_id):
    #     self.orders = [x for x in self.orders if x.order_id != order_id and x.agent_id != agent_id]
    #
    # def age_all_orders(self):
    #     for order in self.orders:
    #         order.time += 1
    #
    # def get_matched_trades(self, tolerance = 0.1):
    #     matched_trades = []
    #     sells = [x for x in self.orders if x.side == 'sell']
    #     buys = [x for x in self.orders if x.side == 'buy']
    #     if buys and sells:
    #         sells = sorted(sells, key=lambda x: (x.price, x.quantity), reverse=False)
    #         buys = sorted(buys, key=lambda x: (x.price, x.quantity), reverse=True)
    #
    #         for sell in sells:
    #             for buy in buys:
    #                 if abs(sell.price - buy.price) > tolerance:
    #                     break
    #                 else:
    #                     agreed_price = (sell.price + buy.price)/2
    #
    #                     if sell.quantity > buy.quantity:
    #                         n_traded_shares = buy.quantity
    #                         matched_trades.append(Trade(buy.agent_id, n_traded_shares, agreed_price, 0))
    #                         matched_trades.append(Trade(sell.agent_id, -n_traded_shares, agreed_price, 0))
    #
    #                         self.remove_order(buy.agent_id, buy.order_id)
    #                         sell.quantity -= n_traded_shares
    #                         self.remove_order(sell.agent_id, sell.order_id)
    #                         self.add_order(Order(sell.agent_id, sell.order_id, sell.side,
    #                                              sell.order_type, sell.quantity, sell.time))
    #                         #remove buy
    #                         buys = [x for x in buys if x.order_id != buy.order_id and x.agent_id != buy.order_id]
    #
    #                     if sell.quantity < buy.quantity:
    #                         n_traded_shares = sell.quantity
    #                         matched_trades.append(Trade(buy.agent_id, n_traded_shares, agreed_price, 0))
    #                         matched_trades.append(Trade(sell.agent_id, -n_traded_shares, agreed_price, 0))
    #
    #                         self.remove_order(sell.agent_id, sell.order_id)
    #                         buy.quantity -= n_traded_shares
    #                         self.remove_order(buy.agent_id, buy.order_id)
    #                         self.add_order(Order(buy.agent_id, buy.order_id, buy.side,
    #                          buy.order_type, buy.quantity, buy.time))
    #                         break
    #
    #                     if sell.quantity == buy.quantity:
    #                         n_traded_shares = sell.quantity
    #                         matched_trades.append(Trade(buy.agent_id, n_traded_shares, agreed_price, 0))
    #                         matched_trades.append(Trade(sell.agent_id, -n_traded_shares, agreed_price, 0))
    #
    #                         self.remove_order(buy.agent_id, buy.order_id)
    #                         self.remove_order(sell.agent_id, sell.order_id)
    #                         #remove buy
    #                         buys = [x for x in buys if x.order_id != buy.order_id and x.agent_id != buy.order_id]
    #                         break
    #
    #                     # self.settled_trades.loc[max(self.settled_trades.index)+1] = \
    #                     # [self.current_step, agreed_price, n_traded_shares]
    #     return matched_trades


# class Trade:
#     def __init__(self, agent_id, quantity, price, time):
#         self.agent_id = agent_id
#         self.quantity = quantity
#         self.price = price
#         self.time = time