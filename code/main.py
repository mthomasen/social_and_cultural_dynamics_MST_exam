from model import SustainableEatingModel
import pandas as pd
import os
from datetime import datetime

# Base parameters
base_params = {
    "num_agents": 100,
    "network_type": "small_world",
    "average_degree": 4,
    "rewiring_prob": 0.1,
    "steps": 50
}

# Scenarios to run
scenarios = ["social", "campaign", "economic"]

# Create output folder if it doesn't exist
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)

# Create timestamp, format: DDMMYYYY-HHMMSS
timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")

# Run each scenario and save results
for scenario in scenarios:
    print(f"Running scenario: {scenario}")
    
    # Initialize model
    params = base_params.copy()
    params["scenario"] = scenario
    model = SustainableEatingModel(**params)

    # Run simulation
    for _ in range(params["steps"]):
        model.step()

    # Save results
    df = pd.DataFrame(model.datacollector.get_model_vars_dataframe())
    df["Scenario"] = scenario
    filename = os.path.join(data_dir, f"sustainable_eating_{scenario}_{timestamp}.csv")
    df.to_csv(filename, index=False)

    print(f"Finished scenario: {scenario}. Results saved to {filename}")