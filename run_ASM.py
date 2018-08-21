import matplotlib.pyplot as mpl

from model import MarketModel

model = MarketModel(1000)
for i in range(200):
    model.step()
    # if not i % 10:
    # 	#print(model.stock.price)
    # 	print(model.stock.price_MA_5)

vs = [v for k, v in model.stock.price_hist.items()]
ks = [k for k, v in model.stock.price_hist.items()]
_10s = [m for k, m in model.stock.price_MA_10_hist.items()]
_50s = [m for k, m in model.stock.price_MA_50_hist.items()]

mpl.plot(ks, vs)
mpl.plot(ks, _10s)
mpl.plot(ks, _50s)
mpl.show()