import typing
import numpy as np

import os
import sys

# 1. Diciamo a Python dove si trova la radice del progetto (Mesa_project)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. IMPORT ASSOLUTI (Risolve l'errore del punto iniziale)
from myExamples.pd_grid_teams.agents import PDAgent
from Mesa_analysis.cooperativeExtension import cooperativeExtension

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)


import mesa
from mesa.discrete_space import OrthogonalMooreGrid


N_ROWS_COLUMNS = 30




TEAM_ARRANGEMENTS = {
    "Head to Head": 0,
    "Checker board": 1,
    "Alternated columns": 2,
    "Random" : 3,
    "Head to Head alternated borders" : 4,
}

class PdGrid1(mesa.Model,cooperativeExtension):
    """Model class for iterated, spatial prisoner's dilemma model."""

    activation_regimes: typing.ClassVar[list[str]] = [
        "Sequential",
        "Random",
        "Simultaneous",
    ]

    # This dictionary holds the payoff for this agent,
    # keyed on: (my_move, other_move)



    payoff_teammates: typing.ClassVar[dict[tuple[str, str], float]] = {
        ("C", "C"): 1,
        ("C", "D"): 0.5,
        ("D", "C"): -1,
        ("D", "D"): 0,
    }
    
    payoff_rivals: typing.ClassVar[dict[tuple[str, str], float]] = {
        ("C", "C"): -0.8,
        ("C", "D"): 0,
        ("D", "C"): 1.6,
        ("D", "D"): 0,
    }

    grid_arrangement = "Head to Head"


    def __init__(
        self, fixed_agentID, fixed_strategy, size=N_ROWS_COLUMNS, activation_order="Random", rng=None,
            
    ):
        """
        Create a new Spatial Prisoners' Dilemma Model.

        Args:
            width, height: Grid size. There will be one agent per grid cell.
            activation_order: Can be "Sequential", "Random", or "Simultaneous".
                           Determines the agent activation regime.
            payoffs: (optional) Dictionary of (move, neighbor_move) payoffs.
        """
        # Convert rng to an integer if it's a string, 
        # or default to 42 if it's missing/empty
        try:
            clean_rng = int(rng) if rng is not None else 42
        except (ValueError, TypeError):
            clean_rng = 42
            
        # Pass the cleaned integer to Mesa's Model class
        super().__init__(rng=clean_rng)

        self.activation_order = activation_order
        self.grid = OrthogonalMooreGrid((size, size), torus=True, random=self.random)
        self.n_teams = 2
        self.teams = [0,1]
        self.teamA = 0
        self.teamB = 1
        self.teamA_score = 0
        self.teamB_score = 0
        self.teamA_score_last = 0
        self.teamB_score_last = 0
        self.stabilization_time = 20
        self.fixed_agentID = fixed_agentID


        agents = PDAgent.create_agents(
            self, len(self.grid.all_cells.cells) ,cell=self.grid.all_cells.cells
        )
        agents[fixed_agentID - 1].change_strategy(fixed_strategy)



        self.datacollector = mesa.DataCollector(
            {
                "Cooperating_Agents": lambda m: len(
                    [a for a in m.agents if a.move == "C"]
                )
            }
        )
        self.running = True
        self.datacollector.collect(self)
        self.coalitions_formation(config=0)

    def decrement_stabilization_time(self):
        self.stabilization_time -= 1
   
    def reset_stabilization_time(self):
        self.stabilization_time = 20
    

    def step(self):
        match self.activation_order:
            case "Sequential":
                # Gli agenti decidono uno dopo l'altro, ma aggiornano solo alla fine
                self.agents.do("step")
                self.agents.do("advance")
                
            case "Random":
                # Ordine casuale di decisione, poi aggiornamento collettivo
                # Questo è il "Random Asynchronous" corretto
                self.agents.shuffle_do("step")
                self.agents.shuffle_do("advance")
                
            case "Simultaneous":
                # Standard Mesa: tutti leggono t, tutti aggiornano a t+1
                self.agents.do("step")
                self.agents.do("advance")
                
            case _:
                raise ValueError(f"Unknown activation order: {self.activation_order}")
            
        self.teamA_score_last = self.teamA_score
        self.teamB_score_last = self.teamB_score
        self.teamA_score = 0
        self.teamB_score = 0

        self.datacollector.collect(self)

    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()
    

    def score(self, move, team, opp_team):
        if team == opp_team:
            return self.payoff_teammates[move]
        else:
            return self.payoff_rivals[move]
    
    def add_score(self,agent,score):
        if agent.team == "A":
            self.teamA_score += score
        else:
            self.teamB_score += score
    


    def n_possible_coalitions(self):
        return 4
    def static_coalitions(self):
        #Coalitions are assigned before preparation's phase
        return True
    
    def preparation_condition(self):
        #Setup ready from the beginning
        return True
    
    
    
    def termination_condition(self):
        
        self.decrement_stabilization_time()
        res = False
        if self.stabilization_time == 0:
            self.reset_stabilization_time()
            res = True
        return res
        
    def coalitions_formation(self,config=0):

        for agent in self.agents:
            team = agent.team_arrangement(config)
            if team == "A":
                self.teamA += 1
            else:
                self.teamB += 1
    
    def player_knockout(self, agent_id):
        self.agents[agent_id - 1].knockout()

    def knockout_IDs(self):
        #They are in the same team in all of the configurations
        #they cover all cases of neighbourhood
        #Team B agents
        #TBD
        agents_IDs = [self.fixed_agentID]
        return agents_IDs

    def payoff(self):
        #Main coalition is team B
        #the payoff is calculated considering B 
        payoff = 0
        score_A = 0
        score_B = 0
        tmp_score = 0
        for agent in self.agents:
            tmp_score = agent.personal_score()
            if agent.team == "A":
                score_A += tmp_score
            elif agent.team == "B":
                score_B += tmp_score
        payoff = score_B - score_A
        return payoff
    
    def print_info(self,agentId):
        #for strategies
        agent = self.agents[agentId - 1]
        res = "Strategy: " + agent.strategy_name()
        return  res
    