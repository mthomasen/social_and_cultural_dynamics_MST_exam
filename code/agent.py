
from mesa import Agent
import random
from functions_and_parameters import CAMPAIGN_STRENGTH, compute_price_effect

class EaterAgent(Agent):
    def __init__(self, unique_id, model, scenario):
        super().__init__(unique_id, model)
        self.scenario = scenario

        # 10% early adopters with high sustainability
        if random.random() < 0.1:
            self.sustainability_score = random.uniform(0.7, 1.0)
        else:
            self.sustainability_score = random.uniform(0.0, 0.3)

        # More realistic distributions for traits
        self.habit_strength = random.betavariate(2, 5)  # most agents resist change moderately
        self.threshold = random.uniform(0.3, 0.7)  # peer pressure threshold
        self.campaign_sensitivity = min(1, max(0, random.normalvariate(0.3, 0.2)))
        self.price_sensitivity = min(1, max(0, random.normalvariate(0.4, 0.15)))

        self.neighbors = []
        self.next_score = self.sustainability_score

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors

    def step(self):
        peer_scores = [self.model.schedule.agents[n].sustainability_score for n in self.neighbors]
        if not peer_scores:
            return

        avg_peer_score = sum(peer_scores) / len(peer_scores)
        social_push = avg_peer_score - self.sustainability_score

        adjustment = 0

        # Social influence (only if peer difference > threshold)
        if social_push > self.threshold:
            adjustment += (1 - self.habit_strength) * (social_push - self.threshold)

        # Scenario 2: Campaign effect only between steps 10–30
        if self.scenario == "campaign" and 10 <= self.model.schedule.time <= 30:
            adjustment += self.campaign_sensitivity * CAMPAIGN_STRENGTH

        # Scenario 3: Economic pressure introduced at step 20
        if self.scenario == "economic" and self.model.schedule.time >= 20:
            adjustment += compute_price_effect(self.price_sensitivity)

        # Apply adjustment, keeping score in [0, 1]
        self.next_score = min(1.0, max(0.0, self.sustainability_score + adjustment))

    def advance(self):
        self.sustainability_score = self.next_score
