import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from gameController import GameController
from cooperativeExtension import cooperativeExtension
from myExamples.boid_flockers.model_simdbscan import BoidFlockers

gc = GameController(BoidFlockers)



N_SIMULATIONS = 100
KO_AGENT = 13
rng = 149
seed = rng + 1
# seed = 157

parameters = {
    "sim_seed" : seed,
    "rng" : rng,
    "ko_agent": KO_AGENT,
}
m_contr = []
sum = 0
for i in range(N_SIMULATIONS):
    print(i)
    marg_contrib , shap_values = gc.run(parameters=parameters)
    m_contr.append([i,marg_contrib[0][0]])
    sum = sum + marg_contrib[0][0]
    parameters["sim_seed"] += 1



m_contr.sort(key=lambda x: x[1], reverse=True)

# Unpack the couples into separate x and y tuples
x = [v for v in range(N_SIMULATIONS)]
a, y = zip(*m_contr)
shap_val = sum / N_SIMULATIONS
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

print("Max value:", m_contr[0][1],"Sim ", seed + m_contr[0][0] )
print("Min value:",m_contr[N_SIMULATIONS - 1][1], "Sim", seed + m_contr[N_SIMULATIONS - 1][0])