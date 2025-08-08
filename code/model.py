from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from agent import EaterAgent
from functions_and_parameters import (
    generate_multiplex, OFFLINE_WEIGHT, ONLINE_WEIGHT, state_to_score, gini, tax_signal
)
import numpy as np

class SustainableEatingModel(Model):
    def __init__(self, num_agents, network_type, average_degree, rewiring_prob, scenario, steps, collect_agents=False):
        super().__init__()
        # keep the signature (network_type/degree not used for multiplex, but kept for API compatibility)
        self.num_agents = num_agents
        self.scenario = scenario
        self.steps = steps
        self.last_velocity = 0.0

        self.schedule = SimultaneousActivation(self)

        # Build multiplex graphs + tribes
        self.G_offline, self.G_online, self.tribes = generate_multiplex(num_agents)

        # Create agents
        for i in range(self.num_agents):
            agent = EaterAgent(i, self, scenario)
            self.schedule.add(agent)
        
        self.id2agent = {a.unique_id: a for a in self.schedule.agents}

        # Assign neighbors for both layers
        for agent in self.schedule.agents:
            off_n = [self.id2agent[i] for i in self.G_offline.neighbors(agent.unique_id)]
            on_n  = [self.id2agent[i] for i in self.G_online.neighbors(agent.unique_id)]
            agent.set_neighbors(off_n, on_n)

        # Data collection & metrics
        self.prev_avg_score = None
        self.current_tax_signal = 0.0
        self.peer_events = 0

        agent_reporters = {} if not collect_agents else {
    "State": "state",
    "Habit": "habit_strength",
    "Threshold": "threshold",
    "Identity": "identity_strength",
}

        self.datacollector = DataCollector(
            model_reporters={
                "AverageSustainability": lambda m: float(np.mean([state_to_score(a.state) for a in m.schedule.agents])),
                "ShareState0": lambda m: np.mean([1.0 if a.state == 0 else 0.0 for a in m.schedule.agents]),
                "ShareState1": lambda m: np.mean([1.0 if a.state == 1 else 0.0 for a in m.schedule.agents]),
                "ShareState2": lambda m: np.mean([1.0 if a.state == 2 else 0.0 for a in m.schedule.agents]),
                "ShareState3": lambda m: np.mean([1.0 if a.state == 3 else 0.0 for a in m.schedule.agents]),
                "GiniScore": lambda m: gini([state_to_score(a.state) for a in m.schedule.agents]),
                "AdoptionVelocity": lambda m: m.last_velocity,
                "PeerInfluenceEvents": lambda m: m.peer_events,
                "TaxSignal": lambda m: m.current_tax_signal,
            },
            agent_reporters=agent_reporters
        )

    def step(self):
    # 1) update tax signal from current adoption (pre-move)
        adoption_share = np.mean([1.0 if a.state >= 1 else 0.0 for a in self.schedule.agents])
        self.current_tax_signal = tax_signal(adoption_share) if self.scenario in ("economic", "combo") else 0.0

    # 2) snapshot avg before move + reset counters
        prev_avg = float(np.mean([state_to_score(a.state) for a in self.schedule.agents]))
        self.peer_events = 0

    # 3) advance one tick
        self.schedule.step()

    # 4) compute velocity after agents moved
        current_avg = float(np.mean([state_to_score(a.state) for a in self.schedule.agents]))
        self.last_velocity = current_avg - prev_avg
        self.prev_avg_score = current_avg  # optional, if you still use it elsewhere

    # 5) NOW collect (captures peer_events of this step)
        self.datacollector.collect(self)
