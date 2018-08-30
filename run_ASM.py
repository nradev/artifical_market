import time
import matplotlib.pyplot as plt

from model import MarketModel

time.clock()

model = MarketModel(n_agents=200,
                    dt=1/252, # 1 business day time step
                    init_rf=0.018,
                    n_shares=1000,
                    init_agent_wealth=1000,#(4*5*1000)/200,
                    glob_risk_aversion=1.5,
                    agent_particip_rate=1,
                    init_price=100,
                    init_dividend=2,
                    dividend_freq=4,
                    dividend_growth=0.05,
                    dividend_vol=0.15,
                    price_adj_speed=0.0000042,
                    max_short=0.01,
                    max_long=0.02)
for i in range(1000):
    model.step()

t1 = time.clock()
print('Model run: {}'.format(round(t1,2)))
#
# vs = [v for k, v in model.stock.price_hist.items()]
# ks = [k for k, v in model.stock.price_hist.items()]
# _50s = [m for k, m in model.stock.price_MA_50_hist.items()]
# plt.plot(ks, vs)
# #plt.plot(ks, _50s)
# plt.show()

model_data = model.datacollector.get_model_vars_dataframe()
agent_data = model.datacollector.get_agent_vars_dataframe()
t2 = time.clock()
print(model_data)
print(agent_data.xs(0, level="AgentID")[["Demand", "Stock Shares", "Target Trade", "Actual Trade", "Cash"]])
t3 = time.clock()

series = ["Price", "Dividend", "Global Wealth", "Agg Buys", "Agg Sells", "Av Buys", "Av Sells",
          "Buy Ratio", "Sell Ratio"]

lw = 0.5
plt.figure("Model", facecolor='w', figsize=(20,11.5) ,frameon=False)
plt.suptitle('This is a somewhat long figure title', fontsize=16)
plt.subplot(321)
plt.plot(model_data[series[0]], linewidth=lw)
plt.title(series[0])
plt.subplot(323)
plt.plot(model_data[series[1]], linewidth=lw)
plt.title(series[1])
plt.subplot(325)
plt.plot(model_data[series[2]], linewidth=lw)
plt.title(series[2])
plt.subplot(322)
plt.plot(model_data[series[3]], 'g', linewidth=lw)
plt.plot(model_data[series[4]], 'r', linewidth=lw)
plt.title("Aggregate Sells/Buys")
plt.subplot(324)
plt.plot(model_data[series[5]], 'g', linewidth=lw)
plt.plot(model_data[series[6]], 'r', linewidth=lw)
plt.title("Available Sells/buys")
plt.subplot(326)
plt.plot(model_data[series[7]], 'g', linewidth=lw)
plt.plot(model_data[series[8]], 'r', linewidth=lw)
plt.title("Sell/Buy Ratios")

for agent in range(1):
    plt.figure(agent, facecolor='w', figsize=(10,11.5) ,frameon=False)
    plt.subplot(511)
    plt.plot(agent_data.xs(agent, level="AgentID")["Wealth"], linewidth=lw)
    plt.ylabel("Wealth")
    plt.subplot(512)
    plt.plot(agent_data.xs(agent, level="AgentID")["Cash"], linewidth=lw)
    plt.ylabel("Cash")
    plt.subplot(513)
    plt.plot(agent_data.xs(agent, level="AgentID")["Stock Weight"], linewidth=lw)
    plt.ylabel("Stock Weight")
    plt.subplot(514)
    plt.plot(agent_data.xs(agent, level="AgentID")["Price Expectation"], linewidth=lw)
    plt.ylabel("Price Expectation")
    plt.subplot(515)
    #plt.plot(agent_data.xs(agent, level="AgentID")["Demand"], linewidth=lw)
    plt.plot(agent_data.xs(agent, level="AgentID")["Target Trade"], linewidth=lw)
    plt.plot(agent_data.xs(agent, level="AgentID")["Actual Trade"], linewidth=lw+0.5)
    plt.ylabel("Target/Actual Trade")
t4 = time.clock()
print('Run model: {}\nGet data frames: {}\nPrint: {}\nPlot: {}\nTotal: {}'
      .format(round(t1,2),round(t2-t1,2),round(t3-t2,2),round(t4-t3,2),round(t4,2)))
plt.show()