import matplotlib.pyplot as mpl

from model import MarketModel

model = MarketModel(n_agents = 200,
                    init_rf = 0.02,
                    n_shares = 1000,
                    glob_risk_aversion = 0.05,
                    init_price = 50,
                    init_dividend = 0.2,
                    dividend_growth = 0.05,
                    dividend_vol = 0.05,
                    price_adj_speed = 0.000001,
                    max_short = 0.01,
                    max_long = 0.02)
for i in range(1000):
    model.step()
    if not i % 10:
        print("p: {}\td: {}".format(round(model.stock.price,2), round(model.stock.dividend,2)))
    # 	print(model.stock.price_MA_5)

vs = [v for k, v in model.stock.price_hist.items()]
ks = [k for k, v in model.stock.price_hist.items()]
_10s = [m for k, m in model.stock.price_MA_10_hist.items()]
_50s = [m for k, m in model.stock.price_MA_50_hist.items()]


mpl.plot(ks, vs)
mpl.plot(ks, _10s)
mpl.plot(ks, _50s)
mpl.show()