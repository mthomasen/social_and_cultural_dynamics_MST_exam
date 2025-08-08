
from mesa import Agent
import random
import numpy as np
from functions_and_parameters import (
    STATE_SCORES, state_to_score,
    THRESHOLD_ALPHA, THRESHOLD_BETA,
    HABIT_ALPHA, HABIT_BETA, HABIT_DECAY,
    IDENTITY_ALPHA, IDENTITY_BETA,
    OFFLINE_WEIGHT, ONLINE_WEIGHT,
    CAMPAIGN_START, CAMPAIGN_END, CAMPAIGN_BASE_STRENGTH, CAMPAIGN_HALF_LIFE,
    BACKLASH_GAP, BACKLASH_SCALE,
    logistic, exp_decay
)


class EaterAgent(Agent):
    def __init__(self, unique_id, model, scenario):
        super().__init__(unique_id, model)
        self.scenario = scenario

        # Initial state: 10% state 1 (flexitarian), 2% state 2 (vegetarian), others at state 0 (omnivorse)
        r = random.random()
        if r < 0.02:
            self.state = 2
        elif r < 0.12:
            self.state = 1
        else:
            self.state = 0
 
        # Priors
        self.habit_strength = np.random.beta(HABIT_ALPHA, HABIT_BETA)
        self.threshold = np.random.beta(THRESHOLD_ALPHA, THRESHOLD_BETA)
        self.identity_strength = np.random.beta(IDENTITY_ALPHA, IDENTITY_BETA)

        # Heterogeneous sensitivities
        self.campaign_sensitivity = max(0.0, np.random.lognormal(mean=-0.2, sigma=0.5))  # ~0-2
        self.econ_sensitivity = float(np.clip(np.random.normal(1.0, 0.25), 0.2, 2.0))

        self.offline_neighbors = []
        self.online_neighbors = []
        self.next_state = self.state

    def set_neighbors(self, offline, online):
        self.offline_neighbors = offline or []
        self.online_neighbors  = online or []

    def _neighbor_mean_state(self):
        off_mean = np.mean([nbr.state for nbr in self.offline_neighbors]) if self.offline_neighbors else self.state
        on_mean  = np.mean([nbr.state for nbr in self.online_neighbors])  if self.online_neighbors  else self.state
        return OFFLINE_WEIGHT * off_mean + ONLINE_WEIGHT * on_mean

    def _campaign_adjustment(self, t):
        if self.scenario in ("campaign", "combo") and (CAMPAIGN_START <= t <= CAMPAIGN_END):
            return self.campaign_sensitivity * CAMPAIGN_BASE_STRENGTH * exp_decay(t, CAMPAIGN_START, CAMPAIGN_HALF_LIFE)
        return 0.0

    def _economic_adjustment(self):
        if self.scenario in ("economic", "combo"):
            return self.econ_sensitivity * self.model.current_tax_signal
        return 0.0

    def _maybe_backlash(self, social_signal):
        gap = social_signal - float(self.state)
        if gap >= BACKLASH_GAP:
            # probabilistic backlash driven by identity
            p = BACKLASH_SCALE * self.identity_strength * logistic(gap - BACKLASH_GAP)
            if np.random.random() < p:
                self.threshold = float(np.clip(self.threshold + 0.05 * gap, 0, 1))
                if self.state > 0 and np.random.random() < 0.5 * self.identity_strength:
                    self.next_state = self.state - 1
                    self.model.peer_events += 1

    def step(self):
        t = self.model.schedule.time
        social_signal = self._neighbor_mean_state()

        # potential backlash first
        self._maybe_backlash(social_signal)

        # pressure to move up one state
        nudges = self._campaign_adjustment(t) + self._economic_adjustment()
        pressure = (social_signal - float(self.state)) + nudges

        effective_threshold = self.threshold * (1.0 + self.habit_strength)

        p_up = logistic(2.5 * (pressure - effective_threshold))
        p_down = logistic(2.0 * ((-pressure) - 0.5 * self.habit_strength))

        rnd = np.random.random()
        self.next_state = self.state
        if rnd < p_up and self.state < 3:
            self.next_state = self.state + 1
            self.model.peer_events += 1
        elif rnd > 1 - p_down and self.state > 0:
            self.next_state = self.state - 1
            self.model.peer_events += 1

        # Habit decays slightly every step
        self.habit_strength *= HABIT_DECAY

    def advance(self):
        self.state = int(self.next_state)
