import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from gameController import GameController
from cooperativeExtension import cooperativeExtension

from myExamples.pd_grid_teams.model_interface_ready_sim2 import PdGrid1







#Simulations for plot PDGRID

SEED = 42
AGENT_ID = 461
STRATEGIES = [ "Balanced", "Selfish", "TeamDevote", "OpponentHater" ]
STRATEGY = STRATEGIES[2]
FIXED_CONFIG = True
CONFIG = 0
#0 H2H, 1 CHECKERBOARD, 2 ALT_COLUMNS, 3 RANDOM
MARGINAL_CONTRIBUTIONS = []
N_SIMULATIONS = 100
#Dictionary
parameters= {
    "fixed_agentID" : AGENT_ID, 
    "fixed_strategy" : STRATEGY,
    "rng" : SEED,
}
gc = GameController(PdGrid1)

for i in range(N_SIMULATIONS):
    marg_contrib, x = gc.run(FIXED_CONFIG, CONFIG, parameters)
    MARGINAL_CONTRIBUTIONS.append((i,marg_contrib[0]))
    parameters["rng"] = parameters["rng"] + 1
    print(i)
    
MARGINAL_CONTRIBUTIONS.sort(key=lambda x: x[1], reverse=True)

# Unpack the couples into separate x and y tuples
x = [v for v in range(N_SIMULATIONS)]
a, y = zip(*MARGINAL_CONTRIBUTIONS)
sum_mg = 0

for e in y:
    sum_mg += e[0]

shap_val = sum_mg / N_SIMULATIONS
std_dev = np.std(y)
# Now you can plot them directly
plt.figure(figsize=(9, 5))

plt.plot(x, y, color='blue')
plt.text(0.95, 0.95, 
         (f"Shapley Value: {shap_val:.2f}\n"
          f"Deviazione Standard: {std_dev:.2f}"), 
         fontsize=11, 
         bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.5'),
         transform=plt.gca().transAxes, 
         verticalalignment='top',
         horizontalalignment='right')
plt.show()

print("Max value:", MARGINAL_CONTRIBUTIONS[0][1],"Sim ", SEED + MARGINAL_CONTRIBUTIONS[0][0] )
print("Min value:",MARGINAL_CONTRIBUTIONS[N_SIMULATIONS - 1][1], "Sim", SEED + MARGINAL_CONTRIBUTIONS[N_SIMULATIONS - 1][0])
# print(MARGINAL_CONTRIBUTIONS)







