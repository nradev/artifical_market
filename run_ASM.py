import time
from model import MarketModel
from plotter import Plotter

time.clock()
model = MarketModel(n_agents=200,
                    population_composition={'zero_information': 0.23, 'value': 0.44, 'momentum': 0.33},
                    settle_type='limit',
                    dt=1/252, # 1 business day time step
                    init_rf=0.018,
                    n_shares=1000,
                    init_agent_wealth=1000,
                    glob_risk_aversion=1.5,
                    glob_interact_rate=0.5,
                    agent_particip_rate=1,
                    init_price=100,
                    init_dividend=2,
                    dividend_freq=252, # 252 for daily dividend
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

pl = Plotter(model)
t2 = time.clock()

pl.print_summary()
pl.plot_model_vars(plot_agg_buy_sell=False)
pl.plot_agent_vars()
pl.plot_network()
pl.show()
t3 = time.clock()

print('Run model: {}\nGet data frames: {}\nPlot: {}\nTotal: {}'
          .format(round(t1,2),round(t2-t1,2),round(t3-t2,2),round(t3,2)))