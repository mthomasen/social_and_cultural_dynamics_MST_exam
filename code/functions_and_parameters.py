import math
import random
import networkx as nx
import numpy as np
import pandas as pd
import os

# ----------------------------
# Behavioural states (discrete)
# ----------------------------
# 0 = omnivore, 1 = flexitarian, 2 = vegetarian, 3 = zero-waste/locavore
STATE_SCORES = [0.20, 0.50, 0.78, 1.00]
def state_to_score(s:int) -> float:
    return STATE_SCORES[int(s)]

# ----------------------------
# Priors 
# ----------------------------
# Threshold ~ Beta(2.5, 3.5) => mean ≈ 0.42 (how far peers must exceed you)
THRESHOLD_ALPHA, THRESHOLD_BETA = 2.5, 3.5
# Habit ~ Beta(3, 7) => mean ≈ 0.30 (resistance to change) with decay per step
HABIT_ALPHA, HABIT_BETA = 3.0, 7.0
HABIT_DECAY = 0.99
# Identity (backlash propensity) ~ Beta(2, 6) => mean ≈ 0.25
IDENTITY_ALPHA, IDENTITY_BETA = 2.0, 6.0

# ----------------------------
# External pressure parameters
# ----------------------------
# Campaign (heterogeneous + time-decaying)
CAMPAIGN_START = 10
CAMPAIGN_END   = 30
CAMPAIGN_BASE_STRENGTH = 0.22
CAMPAIGN_HALF_LIFE = 14.0

# Economic scenario (endogenous to adoption)
TAX_MAX   = 0.30
TAX_PIVOT = 0.55
TAX_K     = 10.0
def tax_signal(adoption_share: float) -> float:
    x = TAX_K * (adoption_share - TAX_PIVOT)
    return TAX_MAX / (1.0 + math.exp(-x))

# Backlash controls
BACKLASH_GAP = 1.2  # trigger if neighbour mean state exceeds mine by >= this
BACKLASH_SCALE = 0.3

# ----------------------------
# Network generation
# ----------------------------

def generate_network(network_type, num_agents, average_degree, rewiring_prob):
    # Keep original function (compatibility), used for single-layer
    if network_type == "small_world":
        return nx.watts_strogatz_graph(num_agents, average_degree, rewiring_prob)
    elif network_type == "random":
        prob = average_degree / (num_agents - 1)
        return nx.erdos_renyi_graph(num_agents, prob)
    elif network_type == "scale_free":
        return nx.barabasi_albert_graph(num_agents, max(1, average_degree // 2))
    else:
        raise ValueError(f"Unknown network type: {network_type}")

# Multiplex: offline (homophily) + online (scale-free reach)
HOMOPHILY_P_SAME = 0.12
HOMOPHILY_P_DIFF = 0.03
N_TRIBES = 3
OFFLINE_WEIGHT = 0.7
ONLINE_WEIGHT  = 0.3

def generate_multiplex(num_agents: int, seed=None):
    # use globally seeded numpy RNG for reproducibility
    rng = np.random
    tribes = rng.randint(0, N_TRIBES, size=num_agents)

    # Offline: homophilous random graph
    G_off = nx.Graph()
    G_off.add_nodes_from(range(num_agents))
    for i, t in enumerate(tribes):
        G_off.nodes[i]["tribe"] = int(t)
    for i in range(num_agents):
        for j in range(i+1, num_agents):
            same = (tribes[i] == tribes[j])
            p = HOMOPHILY_P_SAME if same else HOMOPHILY_P_DIFF
            if rng.rand() < p:
                G_off.add_edge(i, j)

    # connect components if needed (unchanged)
    comps = list(nx.connected_components(G_off))
    if len(comps) > 1:
        nodes = [list(c)[0] for c in comps]
        for a, b in zip(nodes[:-1], nodes[1:]):
            G_off.add_edge(a, b)

    # Online: Barabási–Albert with a deterministic seed
    ba_seed = int(np.random.randint(0, np.iinfo(np.int32).max))  
    G_on = nx.barabasi_albert_graph(num_agents, m=2, seed=ba_seed)
    return G_off, G_on, tribes
# ----------------------------
# Data collection setup
# ----------------------------

def logistic(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))

def exp_decay(t, t0, half_life):
    if t < t0: 
        return 0.0
    return math.exp(-math.log(2) * (t - t0) / float(half_life))

def gini(arr) -> float:
    a = np.array(arr, dtype=float)
    if a.size == 0:
        return 0.0
    if np.amin(a) < 0:
        a = a - np.amin(a)
    mean = np.mean(a)
    if mean == 0:
        return 0.0
    a_sorted = np.sort(a)
    n = a_sorted.size
    cum = np.cumsum(a_sorted)
    return (n + 1 - 2 * np.sum(cum) / cum[-1]) / n


def get_agent_reporters():

    return {
        "State": lambda a: a.state,
        "Habit": lambda a: a.habit_strength,
        "Threshold": lambda a: a.threshold,
        "CampaignSensitivity": lambda a: a.campaign_sensitivity,
        "PriceSensitivity": lambda a: a.econ_sensitivity,
        "Identity": lambda a: a.identity_strength,
    }

def write_endpoint_summary(summaries: dict, data_dir: str, timestamp: str, n_runs_main: int, target: float = 0.80):

    rows = []
    for scenario, df in summaries.items():
        # Final row (max step)
        last_step = int(df["Step"].max())
        last = df[df["Step"] == last_step].iloc[0]
        final_avg = float(last["Avg"])
        final_std = float(last["Std"]) if "Std" in df.columns else float("nan")
        final_ci95 = 1.96 * final_std / np.sqrt(n_runs_main) if final_std == final_std else np.nan

        # Time to reach target average
        hit = df[df["Avg"] >= target]
        t_to_target = float(hit["Step"].iloc[0]) if not hit.empty else float("nan")

        # Peaks
        pv_idx = int(df["Velocity"].idxmax()) if "Velocity" in df.columns else None
        peak_vel = float(df.loc[pv_idx, "Velocity"]) if pv_idx is not None else float("nan")
        peak_vel_step = int(df.loc[pv_idx, "Step"]) if pv_idx is not None else int(last_step)

        pe_idx = int(df["PeerEvents"].idxmax()) if "PeerEvents" in df.columns else None
        peak_events = float(df.loc[pe_idx, "PeerEvents"]) if pe_idx is not None else float("nan")
        peak_events_step = int(df.loc[pe_idx, "Step"]) if pe_idx is not None else int(last_step)

        rows.append({
            "Scenario": scenario,
            "FinalAvg": final_avg,
            "FinalAvgCI95": final_ci95,
            "FinalShare3": float(last["Share3"]),
            "FinalGini": float(last["Gini"]),
            "FinalTaxSignal": float(last["TaxSignal"]),
            f"TimeToTarget(Avg>={target:.2f})": t_to_target,
            "PeakVelocity": peak_vel,
            "PeakVelocityStep": peak_vel_step,
            "PeakPeerEvents": peak_events,
            "PeakPeerEventsStep": peak_events_step,
        })

    endpoints = pd.DataFrame(rows).sort_values("Scenario")
    out_path = os.path.join(data_dir, f"endpoint_summary_{timestamp}.csv")
    endpoints.to_csv(out_path, index=False)
    print(f"Saved endpoint summary: {out_path}")
    return out_path