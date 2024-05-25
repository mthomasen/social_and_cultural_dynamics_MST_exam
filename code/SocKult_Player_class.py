import numpy as np
from scipy.stats import truncnorm, bernoulli

rf_mu = 0.5
rf_sigma = 0.1
rf_lower, rf_upper = 0, 1
rf_a, rf_b = (rf_lower - rf_mu) / rf_sigma, (rf_upper - rf_mu) / rf_sigma

class Player:
    def __init__(self, name, wealth):
        self.name = name
        self.fraction_to_bet = 0.01  # (1%)
        self.bet = wealth * self.fraction_to_bet
        self.choice = 0
        self.risk_factor = truncnorm.rvs(rf_a, rf_b, loc=rf_mu, scale=rf_sigma)
        self.wealth = wealth
        self.player_cards = []

    def adjust_bet(self):
        self.fraction_to_bet = np.random.normal(self.risk_factor * 0.01, 0.01)
        self.fraction_to_bet = max(0.001, min(self.fraction_to_bet, 0.05))
        self.bet = round(self.wealth * self.fraction_to_bet)

    def logistic_function(self, x):
        return 1 / (1 + np.exp(-x))

    def choice_maker(self, sum_of_cards):
        if sum_of_cards >= 21:
            self.choice = 0
        else:
            if sum_of_cards < 16:
                adjusted_risk_factor = self.risk_factor * 0.5
            else:
                adjusted_risk_factor = self.risk_factor
            hit_probability = self.logistic_function(adjusted_risk_factor * (21 - sum_of_cards))
            self.choice = bernoulli.rvs(hit_probability)

    def receive_cards(self, cards):
        self.player_cards.extend(cards)
