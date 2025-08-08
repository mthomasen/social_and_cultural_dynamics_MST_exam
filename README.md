# social\_and\_cultural\_dynamics\_MST\_exam

Here in this GitHub you find all code and data referenced in my paper

Further my zotero library and all referenced papers is also uploaded



Code folder:

* main.py - Imports model, sets key parameters, runs simulation and saves results
* model.py - Mesa model and setup
* agent.py - Agent class with behavioral logic
* functions\_and\_parameters.py - collection of functions and parameters made and used
* plots.py - functions used to generate plots
* sweeps.py - functions used to sweep the backlash, campaign half-life and tax max to look at robustness





The code simulates three scenarios

1. Social - Agents change behavior based only on their peers
2. Campaign - And educational push is active at certain steps
3. Economic - A tax shift happens, meaning a change in food prices
4. Combo - There is both implemented a campaign and a change in food prices



All agents start with a certain diet, omnivore, flexitarian or vegetarian not and have unique traits like habit strength, sensitivity to prices and they openness to campaigns, the changes in their eating behavior is based on peer presure, educational campaigns and difference in food prices





