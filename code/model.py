
from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from agent import EaterAgent
from functions_and_parameters import generate_network, get_model_reporters, get_agent_reporters
import random

class SustainableEatingModel(Model):
    def __init__(self, num_agents, network_type, average_degree, rewiring_prob, scenario, steps):
        super().__init__()
        random.seed(42)  # For reproducibility

        self.num_agents = num_agents
        self.network_type = network_type
        self.average_degree = average_degree
        self.rewiring_prob = rewiring_prob
        self.scenario = scenario
        self.steps = steps

        # Scheduler activates all agents simultaneously
        self.schedule = SimultaneousActivation(self)

        # Generate network structure
        self.G = generate_network(network_type, num_agents, average_degree, rewiring_prob)

        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters=get_model_reporters(),
            agent_reporters=get_agent_reporters()
        )

        # Create and add agents
        for i in range(self.num_agents):
            agent = EaterAgent(i, self, scenario)
            self.schedule.add(agent)

        # Assign network neighbors to each agent
        for agent in self.schedule.agents:
            agent.set_neighbors(list(self.G.neighbors(agent.unique_id)))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
