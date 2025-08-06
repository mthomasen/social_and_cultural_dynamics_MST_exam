# social\_and\_cultural\_dynamics\_MST\_exam

Here in this GitHub you find all code and data referenced in my paper

Further my zotero library and all referenced papers is also uploaded



Code folder:

* main.py - Imports model, sets key parameters, runs simulation and saves results
* model.py - Mesa model and setup
* agent.py - Agent class with behavioral logic
* functions\_and\_parameters.py - collection of functions and parameters made and used



Data

There is one csv for each scenario all containing 

* step number
* Agent ID
* Sustainability score
* Habit 
* Threshold 
* CampaignSensitivity
* PriceSensitivity
* Scenario
* AverageSustainability (the average sustainability across all agents at this step)



The code simulates three scenarios 

1. Social - Agents change behavior based only on their peers
2. Campaign - And educational push is active between time steps 10-30
3. Economic - A tax shift starts at step 20, meaning changes in food prices



All agents start with a certain diet, some sustainable, some not and have unique traits like habit strength, sensitivity to prices and they openness to campaigns, the changes in their eating behavior is based on peer presure, educational campaigns and difference in food prices



to run the simulation it is required to install the following listed packages using pip install, before running the main.py file

* mesa
* network
* pandas
* matplotlib





