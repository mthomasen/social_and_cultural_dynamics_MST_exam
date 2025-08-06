from mesa import Agent
import random

class EaterAgent(Agent):
    def __init__(self, unique_id, model, scenario):
        super().__init__(unique_id, model)
        self.scenario = scenario
        self.sustainability_score = random.uniform(0, 0.3)  # start mostly unsustainable
        self.habit_strength = random.uniform(0.2, 0.8)
        self.threshold = random.uniform(0.3, 0.7)
        self.campaign_sensitivity = random.uniform(0, 0.5)
        self.price_sensitivity = random.uniform(0, 1)
        self.neighbors = []
        self.next_score = self.sustainability_score

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors

    def step(self):
        peer_scores = [self.model.schedule.agents[n].sustainability_score for n in self.neighbors]
        if not peer_scores:
            return

        avg_peer_score = sum(peer_scores) / len(peer_scores)
        influence = avg_peer_score - self.sustainability_score

        # Start with social influence only
        adjustment = 0
        if influence > self.threshold:
            adjustment += (1 - self.habit_strength) * influence

        # Scenario 2: Campaign effect
        if self.scenario == "campaign":
            adjustment += self.campaign_sensitivity * 0.1  # base campaign strength

        # Scenario 3: Economic incentives
        if self.scenario == "economic":
            price_effect = (0.5 * self.price_sensitivity)  # abstracted price effect
            adjustment += price_effect

        self.next_score = min(1.0, max(0.0, self.sustainability_score + adjustment))

    def advance(self):
        self.sustainability_score = self.next_score
        