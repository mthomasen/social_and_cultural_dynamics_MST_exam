# social\_and\_cultural\_dynamics\_MST\_exam

Here in this GitHub you find all code and data referenced in my paper

Further my zotero library and all referenced papers is also uploaded



Code :

* code/main.py – runs 4 scenarios (social/campaign/economic/combo), saves CSVs, figures, and endpoint summary.
* code/model.py – Mesa model setup (multiplex network, schedule, DataCollector).
* code/agent.py – behavioral rules (four states 0–3, habit/threshold/identity, peer backlash).
* code/functions\_and\_parameters.py – parameters, multiplex generator, metrics (Gini, tax signal).
* code/plots.py – helper functions for CI trend, state shares, velocity, peer events, Gini, tax signal.
* code/sweeps.py – parameter sweeps (+ 95% CIs): BACKLASH\_SCALE, CAMPAIGN\_HALF\_LIFE, TAX\_MAX.



The code simulates three scenarios

1. Social - Agents change behavior based only on their peers
2. Campaign - And educational push is active at certain steps
3. Economic - A tax shift happens, meaning a change in food prices
4. Combo - There is both implemented a campaign and a change in food prices



All agents start with a certain diet, omnivore, flexitarian or vegetarian not and have unique traits like habit strength, sensitivity to prices and they openness to campaigns, the changes in their eating behavior is based on peer presure, educational campaigns and difference in food prices

