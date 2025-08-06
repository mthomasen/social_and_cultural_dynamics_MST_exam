from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from agent import EaterAgent
from functions_and_parameters import generate_network, get_agent_reporters, get_model_reporters


class SustainableEatingModel(Model):
    def __init__(self, num_agents, network_type, average_degree, rewiring_prob, scenario, steps):
        super().__init__()
        self.num_agents = num_agents
        self.network_type = network_type
        self.average_degree = average_degree
        self.rewiring_prob = rewiring_prob
        self.scenario = scenario
        self.schedule = SimultaneousActivation(self)
        self.steps = steps

        self.G = generate_network(network_type, num_agents, average_degree, rewiring_prob)
        self.datacollector = DataCollector(
            model_reporters=get_model_reporters(),
            agent_reporters=get_agent_reporters()
            )

        # Create agents
        for i in range(self.num_agents):
            agent = EaterAgent(i, self, scenario)
            self.schedule.add(agent)
        
        # Link agents to network
        for agent in self.schedule.agents:
            agent.set_neighbors(list(self.G.neighbors(agent.unique_id)))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

