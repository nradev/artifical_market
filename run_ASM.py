import time
import matplotlib.pyplot as plt

from model import MarketModel

time.clock()

model = MarketModel(n_agents=200,
                    init_rf=0.001,
                    n_shares=1000,
                    init_agent_wealth=1000,#(4*5*1000)/200,
                    glob_risk_aversion=5,
                    init_price=50,
                    init_dividend=2,
                    dividend_growth=0.1,
                    dividend_vol=0.1,
                    price_adj_speed=0.000001,
                    max_short=0.01,
                    max_long=0.02)
for i in range(1000):
    model.step()

print(time.clock())
#
# vs = [v for k, v in model.stock.price_hist.items()]
# ks = [k for k, v in model.stock.price_hist.items()]
# _50s = [m for k, m in model.stock.price_MA_50_hist.items()]
# plt.plot(ks, vs)
# #plt.plot(ks, _50s)
# plt.show()

model_data = model.datacollector.get_model_vars_dataframe()
agent_data = model.datacollector.get_agent_vars_dataframe()
print(model_data)
print(agent_data.xs(0, level="AgentID")[["Demand", "Stock Shares", "Target Trade", "Actual Trade", "Cash"]])

lw = 1
plt.figure(100, facecolor='w', figsize=(10,11.5) ,frameon=False)
plt.subplot(311)
plt.plot(model_data["Price"], linewidth=lw)
plt.subplot(312)
plt.plot(model_data["Dividend"], linewidth=lw)
plt.subplot(313)
plt.plot(model_data["Global Wealth"], linewidth=lw)

plt.figure(101, facecolor='w', figsize=(10,11.5) ,frameon=False)
plt.subplot(311)
plt.plot(model_data["Agg Buys"], 'g', linewidth=lw)
plt.plot(model_data["Agg Sells"], 'r', linewidth=lw)
plt.subplot(312)
plt.plot(model_data["Av Buys"], 'g', linewidth=lw)
plt.plot(model_data["Av Sells"], 'r', linewidth=lw)
plt.subplot(313)
plt.plot(model_data["Buy Ratio"], 'g', linewidth=lw)
plt.plot(model_data["Sell Ratio"], 'r', linewidth=lw)

for agent in range(1):
    plt.figure(agent, facecolor='w', figsize=(10,11.5) ,frameon=False)
    plt.subplot(511)
    plt.plot(agent_data.xs(agent, level="AgentID")["Wealth"], linewidth=lw)
    plt.subplot(512)
    plt.plot(agent_data.xs(agent, level="AgentID")["Cash"], linewidth=lw)
    plt.subplot(513)
    plt.plot(agent_data.xs(agent, level="AgentID")["Stock Weight"], linewidth=lw)
    plt.subplot(514)
    plt.plot(agent_data.xs(agent, level="AgentID")["Price Expectation"], linewidth=lw)
    plt.subplot(515)
    #plt.plot(agent_data.xs(agent, level="AgentID")["Demand"], linewidth=lw)
    plt.plot(agent_data.xs(agent, level="AgentID")["Target Trade"], linewidth=lw)
    plt.plot(agent_data.xs(agent, level="AgentID")["Actual Trade"], linewidth=lw+0.5)
print(time.clock())
plt.show()
