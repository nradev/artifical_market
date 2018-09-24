import matplotlib.pyplot as plt
import networkx as nx


class Plotter:
    def __init__(self, model):
        self.model = model
        self.model_data = model.datacollector.get_model_vars_dataframe()
        self.agent_data = model.datacollector.get_agent_vars_dataframe()

    def print_summary(self):
        print(self.model_data)
        print(
            self.agent_data.xs(0, level="AgentID")[["Demand", "Stock Shares", "Target Trade", "Actual Trade", "Cash"]])

    def plot_model_vars(self, plot_agg_buy_sell=True):
        series = ["Price", "Return", "Dividend", "Agg Buys", "Agg Sells", "Av Buys", "Av Sells",
                  "Buy Ratio", "Sell Ratio", "Vol", "Skew", "Kurt"]
        lw = 0.5
        plt.figure("Model", facecolor='w', figsize=(20, 11.5), frameon=False)
        plt.suptitle('Model Vars', fontsize=16)
        plt.subplot(321)
        plt.plot(self.model_data[series[0]], linewidth=lw)
        plt.title(series[0])
        plt.subplot(323)
        plt.plot(self.model_data[series[1]], linewidth=lw)
        plt.title(series[1])
        plt.subplot(325)
        plt.plot(self.model_data[series[2]], linewidth=lw)
        plt.title(series[2])
        if self.model.settle_type == 'limit' or not plot_agg_buy_sell:
            plt.subplot(322)
            plt.plot(self.model_data[series[9]], linewidth=lw)
            plt.title(series[9])
            plt.subplot(324)
            plt.plot(self.model_data[series[10]], linewidth=lw)
            plt.title(series[10])
            plt.subplot(326)
            plt.plot(self.model_data[series[11]], linewidth=lw)
            plt.title(series[11])
        elif self.model.settle_type == 'market':
            plt.subplot(322)
            plt.plot(self.model_data[series[3]], 'g', linewidth=lw)
            plt.plot(self.model_data[series[4]], 'r', linewidth=lw)
            plt.title("Aggregate Sells/Buys")
            plt.subplot(324)
            plt.plot(self.model_data[series[5]], 'g', linewidth=lw)
            plt.plot(self.model_data[series[6]], 'r', linewidth=lw)
            plt.title("Available Sells/buys")
            plt.subplot(326)
            plt.plot(self.model_data[series[7]], 'g', linewidth=lw)
            plt.plot(self.model_data[series[8]], 'r', linewidth=lw)
            plt.title("Sell/Buy Ratios")


    def plot_agent_vars(self):
        strategies = [key for key in self.model.population_composition]
        agents_to_plot = []
        for s in strategies:
            agents_to_plot.append(
                (s, [agent.agent_id for agent in self.model.schedule.agents if agent.strategy.strat_name == s][0]))

        lw = 0.5
        for strat, agent in agents_to_plot:
            plt.figure(strat, facecolor='w', figsize=(10, 11.5), frameon=False)
            plt.subplot(511)
            plt.plot(self.agent_data.xs(agent, level="AgentID")["Wealth"], linewidth=lw)
            plt.ylabel("Wealth")
            plt.subplot(512)
            plt.plot(self.agent_data.xs(agent, level="AgentID")["Cash"], linewidth=lw)
            plt.ylabel("Cash")
            plt.subplot(513)
            plt.plot(self.agent_data.xs(agent, level="AgentID")["Stock Weight"], linewidth=lw)
            plt.ylabel("Stock Weight")
            plt.subplot(514)
            plt.plot(self.agent_data.xs(agent, level="AgentID")["Price Expectation"], linewidth=lw)
            plt.ylabel("p+d Expectation")
            plt.subplot(515)
            # plt.plot(self.agent_data.xs(agent, level="AgentID")["Demand"], linewidth=lw)
            plt.plot(self.agent_data.xs(agent, level="AgentID")["Target Trade"], linewidth=lw)
            plt.plot(self.agent_data.xs(agent, level="AgentID")["Actual Trade"], linewidth=lw + 0.5)
            plt.ylabel("Target/Actual Trade")

    def plot_network(self):
        plt.figure('Network')
        # node_color = [float(self.model.net.degree(nd)) for nd in self.model.net]

        dt = 1 / len(self.model.population_composition)
        color_key = {}
        for k in self.model.population_composition:
            color_key[k] = dt
            dt += dt
        node_color = [float(color_key[self.model.net.nodes[nd]['strat']]) for nd in self.model.net]
        options = {'node_color': node_color, 'node_size': 250, 'width': .5, 'with_labels': False}
        nx.draw_kamada_kawai(self.model.net, **options)
        # plt.legend(tuple(color_key.keys()),tuple(color_key.values()))
        pos = nx.kamada_kawai_layout(self.model.net)
        labels = nx.get_node_attributes(self.model.net, 'agent_id')
        nx.draw_networkx_labels(self.model.net, pos, labels, font_size=8, font_color='w', font_weight='bold')

    def show(self):
        plt.show()