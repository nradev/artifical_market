import datetime as dt
import random
import numpy


class Agent:
    def __init__(self, agent_id, model):
        self.unique_id = agent_id
        self.model = model

    def step(self):
        pass


class Model:
    def __init__(self, seed=None):
        self.seed = dt.datetime.now() if seed is None else seed
        random.seed(seed)
        numpy.random.seed(seed)
        self.running = True
        self.schedule = None

    def run_model(self):
        while self.running:
            self.step()

    def step(self):
        pass
