import time
import matplotlib.pyplot as plt
from model import MarketModel

time.clock()
model = MarketModel(n_agents=200,
                    population_composition={'zero_information': 0.33, 'value': 0.34, 'momentum': 0.33},
                    settle_type='limit',
                    dt=1/252, # 1 business day time step
                    init_rf=0.018,
                    n_shares=1000,
                    init_agent_wealth=1000,#(4*5*1000)/200,
                    glob_risk_aversion=1.5,
                    glob_interact_rate=0.25,
                    agent_particip_rate=1,
                    init_price=100,
                    init_dividend=2,
                    dividend_freq=4,
                    dividend_growth=0.01,
                    dividend_vol=0.15,
                    div_noise_sig=0.25,
                    price_adj_speed=0.0000042,
                    max_short=0.01,
                    max_long=0.02)
for i in range(500):
    model.step()

t1 = time.clock()
print('Model run: {}'.format(round(t1,2)))
model_data = model.datacollector.get_model_vars_dataframe()
agent_data = model.datacollector.get_agent_vars_dataframe()
t2 = time.clock()
print(model_data)
print(agent_data.xs(0, level="AgentID")[["Demand", "Stock Shares", "Target Trade", "Actual Trade", "Cash"]])
t3 = time.clock()

chart = True
if chart:
    series = ["Price", "Dividend", "Global Wealth", "Agg Buys", "Agg Sells", "Av Buys", "Av Sells",
              "Buy Ratio", "Sell Ratio"]
    lw = 0.5
    plt.figure("Model", facecolor='w', figsize=(20,11.5) ,frameon=False)
    plt.suptitle('Model Vars', fontsize=16)
    plt.subplot(321)
    plt.plot(model_data[series[0]], linewidth=lw)
    plt.title(series[0])
    plt.subplot(323)
    plt.plot(model_data[series[1]], linewidth=lw)
    plt.title(series[1])
    plt.subplot(325)
    plt.plot(model_data[series[2]], linewidth=lw)
    plt.title(series[2])
    if model.settle_type == 'market':
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

    strategies = [key for key in model.population_composition]
    agents_to_plot = []
    for s in strategies:
        agents_to_plot.append((s,[agent.agent_id for agent in model.schedule.agents if agent.strategy.strat_name == s][0]))

    for strat, agent in agents_to_plot:
        plt.figure(strat, facecolor='w', figsize=(10,11.5) ,frameon=False)
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
        plt.ylabel("p+d Expectation")
        plt.subplot(515)
        #plt.plot(agent_data.xs(agent, level="AgentID")["Demand"], linewidth=lw)
        plt.plot(agent_data.xs(agent, level="AgentID")["Target Trade"], linewidth=lw)
        plt.plot(agent_data.xs(agent, level="AgentID")["Actual Trade"], linewidth=lw+0.5)
        plt.ylabel("Target/Actual Trade")
    plt.show()
t4 = time.clock()
print('Run model: {}\nGet data frames: {}\nPrint: {}\nPlot: {}\nTotal: {}'
          .format(round(t1,2),round(t2-t1,2),round(t3-t2,2),round(t4-t3,2),round(t4,2)))