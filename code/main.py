
from model import SustainableEatingModel
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Base simulation parameters
base_params = {
    "num_agents": 100,
    "network_type": "small_world",
    "average_degree": 4,
    "rewiring_prob": 0.1,
    "steps": 50
}

# Define which scenarios to simulate
scenarios = ["social", "campaign", "economic"]

# Create data folder (one level above code) if it doesn't exist
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)

# Generate a timestamp to tag outputs
timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")

# Collect model-level summaries for all scenarios
all_model_dfs = []

# Run simulation for each scenario
for scenario in scenarios:
    print(f"Running scenario: {scenario}")

    # Set scenario-specific model
    params = base_params.copy()
    params["scenario"] = scenario
    model = SustainableEatingModel(**params)

    # Run the model for defined steps
    for _ in range(params["steps"]):
        model.step()

    # Extract data
    agent_df = model.datacollector.get_agent_vars_dataframe()
    model_df = model.datacollector.get_model_vars_dataframe()

    # Reset index so Step and AgentID become columns
    agent_df.index.names = ["Step", "AgentID"]
    agent_df = agent_df.reset_index()
    model_df.index.name = "Step"
    model_df = model_df.reset_index()

    # Merge agent- and model-level data
    combined_df = pd.merge(agent_df, model_df, on="Step", how="left")
    combined_df["Scenario"] = scenario

    # Save combined CSV file
    out_file = os.path.join(data_dir, f"sustainable_eating_{scenario}_{timestamp}.csv")
    combined_df.to_csv(out_file, index=False)
    print(f"Saved results to: {out_file}")

    # Store model-level data for plotting
    all_model_dfs.append(model_df.assign(Scenario=scenario))

# ------------------------------------------
# Plot: Average sustainability across steps
# ------------------------------------------
summary_df = pd.concat(all_model_dfs)

plt.figure(figsize=(10, 6))
for scenario in scenarios:
    data = summary_df[summary_df["Scenario"] == scenario]
    plt.plot(data["Step"], data["AverageSustainability"], label=scenario)

plt.title("Average Sustainability Over Time")
plt.xlabel("Step")
plt.ylabel("Average Sustainability Score")
plt.legend(title="Scenario")
plt.tight_layout()

# Save and show the plot
plot_path = os.path.join(data_dir, f"sustainability_trends_{timestamp}.png")
plt.savefig(plot_path)
plt.show()
print(f"Sustainability trend plot saved to: {plot_path}")
