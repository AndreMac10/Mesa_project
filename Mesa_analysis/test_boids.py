import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from gameController import GameController
from cooperativeExtension import cooperativeExtension
from myExamples.boid_flockers.model_dbscan_edit import BoidFlockers

valid_seeds = [92,125,146,155,173]
#valid_seeds = [125]
# agentID[6,18,6,1,12]
model_class = BoidFlockers

gc = GameController(model_class)
rng = 149
# marg_contrib , shap_values = gc.run(parameters={"rng": rng})

flag = True
"""
for seed in valid_seeds:
    marg_contrib , shap_values = gc.run(parameters={"rng": seed})
"""
while( rng < 1200 and flag ):
    marg_contrib , shap_values = gc.run(parameters={"rng": rng})
    for v in shap_values:
        if abs(v[1]) > 35: 
            flag = False
        
    if flag: rng += 3
if not flag : print(rng)
