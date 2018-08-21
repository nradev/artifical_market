import random


class BaseScheduler:
    def __init__(self, model):
        self.model = model
        self.steps = 0
        self.time = 0
        self.agents = []

    def add(self, agent):
        self.agents.append(agent)

    def add_all(self, agents):
        for x in agents:
            self.add(x)

    def remove(self, agent):
        while agent in self.agents:
            self.agents.remove(agent)

    def step(self):
        for agent in self.agents[:]:
            agent.step()
        self.steps += 1
        self.time += 1

    def get_agent_count(self):
        return len(self.agents)


class RandomActivation(BaseScheduler):
    def step(self):
        random.shuffle(self.agents)
        for agent in self.agents[:]:
            agent.step()
        self.steps += 1
        self.time += 1


class SimultaneousActivation(BaseScheduler):
    def step(self):
        for agent in self.agents[:]:
            agent.step()
        for agent in self.agents[:]:
            agent.advance()
        self.steps += 1
        self.time += 1


class StagedActivation(BaseScheduler):
    def __init__(self, model, no_of_steps, shuffle=False, shuffle_between_stages=False):
        super().__init__(model)
        self.stage_list = ["step_{}".format(i + 1) for i in range(no_of_steps)]
        self.shuffle = shuffle
        self.shuffle_between_stages = shuffle_between_stages
        self.stage_time = 1 / len(self.stage_list)

    def step(self):
        if self.shuffle:
            random.shuffle(self.agents)
        for stage in self.stage_list:
            for agent in self.agents[:]:
                getattr(agent, stage)()  # Run stage
            if self.shuffle_between_stages:
                random.shuffle(self.agents)
            self.time += self.stage_time

        self.steps += 1
