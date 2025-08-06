
import networkx as nx

# ----------------------------
# External pressure parameters
# ----------------------------

CAMPAIGN_STRENGTH = 0.1  # Strength of the campaign's push (used if scenario == 'campaign')

# Economic scenario parameters
BASE_MEAT_PRICE = 1.0
BASE_PLANT_PRICE = 0.7
MEAT_TAX_MULTIPLIER = 1.3  # Meat becomes 30% more expensive
PLANT_SUBSIDY_MULTIPLIER = 0.8  # Plant-based food becomes 20% cheaper

def compute_price_effect(price_sensitivity):
    """
    Calculate the effect of price differences on sustainability behavior.
    Scales with an agent's price_sensitivity.
    """
    taxed_meat_price = BASE_MEAT_PRICE * MEAT_TAX_MULTIPLIER
    subsidized_plant_price = BASE_PLANT_PRICE * PLANT_SUBSIDY_MULTIPLIER
    price_diff = taxed_meat_price - subsidized_plant_price
    return price_diff * price_sensitivity


# ----------------------------
# Network generation
# ----------------------------

def generate_network(network_type, num_agents, average_degree, rewiring_prob):
    if network_type == "small_world":
        return nx.watts_strogatz_graph(num_agents, average_degree, rewiring_prob)
    elif network_type == "random":
        prob = average_degree / (num_agents - 1)
        return nx.erdos_renyi_graph(num_agents, prob)
    elif network_type == "scale_free":
        return nx.barabasi_albert_graph(num_agents, max(1, average_degree // 2))
    else:
        raise ValueError(f"Unknown network type: {network_type}")


# ----------------------------
# Data collection setup
# ----------------------------

def get_model_reporters():
    return {
        "AverageSustainability": lambda m: sum(
            a.sustainability_score for a in m.schedule.agents
        ) / len(m.schedule.agents)
    }

def get_agent_reporters():
    return {
        "Sustainability": lambda a: a.sustainability_score,
        "Habit": lambda a: a.habit_strength,
        "Threshold": lambda a: a.threshold,
        "CampaignSensitivity": lambda a: a.campaign_sensitivity,
        "PriceSensitivity": lambda a: a.price_sensitivity,
        "Scenario": lambda a: a.scenario
    }
