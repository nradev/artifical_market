import matplotlib.pyplot as plt

from model import MarketModel

model = MarketModel(n_agents=200,
                    init_rf=0.02,
                    n_shares=1000,
                    glob_risk_aversion=5,
                    init_price=50,
                    init_dividend=2,
                    dividend_growth=0.5,
                    dividend_vol=0.2,
                    price_adj_speed=0.000001,
                    max_short=0.01,
                    max_long=0.02)
for i in range(100):
    model.step()
#     if not i % 100:
#         min_cash = int(min([agent.cash for agent in model.schedule.agents]))
#         print("p: {}\td: {}\tW: {}\tC_m: {}".format(round(model.stock.price, 2), round(model.stock.dividend, 2),
#                                                     int(model.global_wealth), min_cash))
#
# vs = [v for k, v in model.stock.price_hist.items()]
# ks = [k for k, v in model.stock.price_hist.items()]
# _10s = [m for k, m in model.stock.price_MA_10_hist.items()]
# _50s = [m for k, m in model.stock.price_MA_50_hist.items()]
#
# plt.plot(ks, vs)
# #plt.plot(ks, _10s)
# #plt.plot(ks, _50s)
# plt.show()

model_data = model.datacollector.get_model_vars_dataframe()
agent_data = model.datacollector.get_agent_vars_dataframe()
print(model_data)
print(agent_data.xs(0, level="AgentID")["Wealth"])#,"Cash", "Stock Weight", "Stock Shares",
                                        #"Demand", "Target Trade", "Actual Trade"])
#plt.plot(model_data["Price"], linewidth=lw)

for agent in range(3):
    lw = 1
    plt.figure(agent, facecolor='w', figsize=(10,11.5) ,frameon=False)
    plt.subplot(511)
    plt.plot(agent_data.xs(agent, level="AgentID")["Wealth"], linewidth=lw)
    plt.subplot(512)
    plt.plot(agent_data.xs(agent, level="AgentID")["Cash"], linewidth=lw)
    plt.subplot(513)
    plt.plot(agent_data.xs(agent, level="AgentID")["Stock Weight"], linewidth=lw)
    plt.subplot(514)
    plt.plot(agent_data.xs(agent, level="AgentID")["Stock Shares"], linewidth=lw)
    plt.subplot(515)
    #plt.plot(agent_data.xs(agent, level="AgentID")["Demand"], linewidth=lw)
    plt.plot(agent_data.xs(agent, level="AgentID")["Target Trade"], linewidth=lw)
    plt.plot(agent_data.xs(agent, level="AgentID")["Actual Trade"], linewidth=lw+0.5)
plt.show()
