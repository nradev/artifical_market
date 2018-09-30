import time
from model import MarketModel
from plotter import Plotter
model = MarketModel(n_agents=200,
                    #population_composition={'zero_information': 0.23, 'value': 0.44, 'momentum': 0.33},
                    # population_composition={'zero_information': {'R': 0.03, 'RC': 0.03, 'RO': 0.03, 'L': 0.05, 'LC': 0.05, 'LO': 0.04},
                    #                         'value':            {'R': 0.07, 'RC': 0.07, 'RO': 0.07, 'L': 0.09, 'LC': 0.07, 'LO': 0.07},
                    #                         'momentum':         {'R': 0.05, 'RC': 0.05, 'RO': 0.05, 'L': 0.06, 'LC': 0.06, 'LO': 0.06}},
                    population_composition={'zero_information': {'R': 0.01, 'RC': 0.01, 'RO': 0.01, 'L': 0.06, 'LC': 0.06, 'LO': 0.08},
                                            'value':            {'R': 0.01, 'RC': 0.01, 'RO': 0.01, 'L': 0.15, 'LC': 0.13, 'LO': 0.13},
                                            'momentum':         {'R': 0.01, 'RC': 0.01, 'RO': 0.01, 'L': 0.10, 'LC': 0.10, 'LO': 0.10}},
                    settle_type='limit',
                    dt=1/252, # 1 business day time step
                    init_rf=0.018,
                    n_shares=1000,
                    init_agent_wealth=1000,
                    glob_risk_aversion=1.5,
                    glob_loss_aversion=2.5,
                    confidance_levels=(0.7, 3),
                    glob_interact_rate=0.25,
                    agent_particip_rate=1,
                    init_price=115,
                    init_dividend=2,
                    dividend_freq=252, # 252 for daily dividend
                    dividend_growth=0.01,
                    dividend_vol=0.15,
                    div_noise_sig=0.25,
                    price_adj_speed=0.0000042,
                    max_short=0.01,
                    max_long=0.02)

time.clock()
for i in range(500):
    model.step()
t1 = time.clock()
print('Model run: {}'.format(round(t1,2)))

pl = Plotter(model)
t2 = time.clock()

#pl.print_summary()
pl.plot_model_vars(plot_agg_buy_sell=False)
pl.plot_agent_vars()
#pl.plot_network()
pl.show()
t3 = time.clock()

print('Run model: {}\nGet data frames: {}\nPlot: {}\nTotal: {}'
          .format(round(t1,2),round(t2-t1,2),round(t3-t2,2),round(t3,2)))