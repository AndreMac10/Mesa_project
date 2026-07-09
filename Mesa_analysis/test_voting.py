import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gameController import GameController
from cooperativeExtension import cooperativeExtension
from myExamples.voting_netlogo.model_interface_ready import VotingGrid
from myExamples.voting_netlogo.model_interface_ready_sim1 import VotingGrid1

#SIMULATIONS FOR VOTING 
SEED = 46

gc = GameController(VotingGrid1)
"""
rng = SEED
i = 0
while(rng < 120):

    gc.run(parameters={"rng" : rng})

    #numero di voti per la squadra 1
    initial_score = gc.reference_payoff[i]
    points_to_win = abs(451 - initial_score)
    print(points_to_win)
    rng += 4
    i +=1
"""


gc.run(parameters={"rng" : SEED})
#numero di voti per la squadra 1
initial_score = gc.reference_payoff[0]
points_to_win = abs(451 - initial_score)
winning_team = 0 if initial_score < 450 else 1
losing_team = 0 if winning_team else 1
print("Team 1 has", initial_score, "votes.")
print("Points to do for team", losing_team,"to win :",points_to_win)
team_changing_agents = []

parameters= {
    "winning_team" : winning_team,
    "changing_agents" : team_changing_agents,
    "rng" : SEED,
}


while (points_to_win > 0):
    a, shap_val = gc.run(parameters=parameters)
    points_to_win -= shap_val[0][1] 
    team_changing_agents.append(shap_val[0][0])
    print("Points left for team", winning_team,"to win :",points_to_win)

print(team_changing_agents)
