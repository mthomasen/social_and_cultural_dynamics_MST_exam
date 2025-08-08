from model import SustainableEatingModel
from plots import plot_all
from sweeps import sweep_backlash, sweep_halflife, sweep_taxmax
from functions_and_parameters import write_endpoint_summary
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import random, numpy as np


# Base simulation parameters
base_params = {
    "num_agents": 300,
    "network_type": "small_world",
    "average_degree": 4,
    "rewiring_prob": 0.1,
    "steps": 60,
    "collect_agents": False,  # keep False for speed
}

# Scenarios
scenarios = ["social", "campaign", "economic", "combo"]

# Create data folder and plots subfolder
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
plots_dir = os.path.join(data_dir, "plots")
os.makedirs(data_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")


def run_monte_carlo(scenario, steps, n_runs=100, seed0=123):
    frames = []
    for r in range(n_runs):
        if r % 10 == 0:
            print(f"{scenario}: run {r}/{n_runs}")
        rng_seed = seed0+r
        random.seed(rng_seed)
        np.random.seed(rng_seed)
        params = base_params.copy()
        params["scenario"] = scenario
        model = SustainableEatingModel(**params)
        for _ in range(steps):
            model.step()
        mdf = (
            model.datacollector.get_model_vars_dataframe()
            .reset_index()
            .rename(columns={"index": "Step"})
        )
        mdf["Run"] = r
        frames.append(mdf)

    all_runs = pd.concat(frames, ignore_index=True)

    # aggregate with CI
    agg = (
        all_runs.groupby("Step")
        .agg(
            Avg=("AverageSustainability", "mean"),
            Std=("AverageSustainability", "std"),
            Share0=("ShareState0", "mean"),
            Share1=("ShareState1", "mean"),
            Share2=("ShareState2", "mean"),
            Share3=("ShareState3", "mean"),
            Share3Std = ("ShareState3","Std"),
            Gini=("GiniScore", "mean"),
            Velocity=("AdoptionVelocity", "mean"),
            PeerEvents=("PeerInfluenceEvents", "mean"),
            TaxSignal=("TaxSignal", "mean"),
        )
        .reset_index()
    )
    agg["CI95"] = 1.96 * agg["Std"] / np.sqrt(n_runs)
    return all_runs, agg


# ---------- Run scenarios, save CSVs, make plots ----------

summaries = {}

for scenario in scenarios:
    print(f"Running scenario: {scenario}")
    all_runs, summary = run_monte_carlo(
        scenario, steps=base_params["steps"], n_runs=100   # bump to 100 for finals
    )
    # Save CSVs
    all_runs_out = os.path.join(
        data_dir, f"sustainable_eating_{scenario}_allruns_{timestamp}.csv"
    )
    summary_out = os.path.join(
        data_dir, f"sustainable_eating_{scenario}_summary_{timestamp}.csv"
    )
    all_runs.to_csv(all_runs_out, index=False)
    summary.to_csv(summary_out, index=False)
    print(f"Saved: {all_runs_out}")
    print(f"Saved: {summary_out}")
    summaries[scenario] = summary

# Produce all figures into data/plots/
plot_all(summaries, plots_dir, timestamp)

write_endpoint_summary(
    summaries,
    data_dir,
    timestamp,
    n_runs_main=100,
    target=0.80
)

# ---------- Robustness sweeps (adjust values & n_runs) ----------

backlash_vals = [0.20, 0.25, 0.30, 0.35]
halflife_vals = [6, 10, 14, 18, 22]
taxmax_vals   = [0.24, 0.26, 0.28, 0.30, 0.32]

# Backlash (combo)
sweep_backlash(run_monte_carlo, backlash_vals,
               steps=base_params["steps"], n_runs=30,
               target=0.80, data_dir=data_dir, plot_dir=plots_dir, timestamp=timestamp)

# Campaign half-life (combo)
sweep_halflife(run_monte_carlo, halflife_vals,
               steps=base_params["steps"], n_runs=20,
               target=0.80, data_dir=data_dir, plot_dir=plots_dir, timestamp=timestamp)

# Tax max (combo)
sweep_taxmax(run_monte_carlo, taxmax_vals,
             steps=base_params["steps"], n_runs=20,
             target=0.80, data_dir=data_dir, plot_dir=plots_dir, timestamp=timestamp)

print("Done.")