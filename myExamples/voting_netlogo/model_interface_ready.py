import typing

import os
import sys

# 1. Diciamo a Python dove si trova la radice del progetto (Mesa_project)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. IMPORT ASSOLUTI (Risolve l'errore del punto iniziale)
from myExamples.voting_netlogo.agents import VotingAgent
from ABG_Simulator.cooperativeExtension import cooperativeExtension

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

import mesa
from mesa.discrete_space import OrthogonalMooreGrid

N_ROWS_COLUMNS = 30

# Per formare i team in base alla configurazione di partenza data da TEAM_ARRANGEMENT
TEAMS_FROM_THE_BEGINNING = False

TEAM_ARRANGEMENT = 3
#0  Head to Head
#1  Checker board
#2  Alternated Columns
#3  Random

class VotingGrid(mesa.Model,cooperativeExtension):


    activation_regimes: typing.ClassVar[list[str]] = [
        "Sequential",
        "Random",
        "Simultaneous",
    ]


    def __init__(self, size=N_ROWS_COLUMNS, activation_order="Random",rng = None, change_vote_if_tied=False ):

        try:
            clean_rng = int(rng) if rng is not None else 42
        except (ValueError, TypeError):
            clean_rng = 42
        super().__init__(rng=clean_rng)
        self.n_players = size * size
        self.activation_order = activation_order
        self.grid = OrthogonalMooreGrid((size, size), torus=True, random=self.random)
        

        agents = VotingAgent.create_agents(
            self, len(self.grid.all_cells.cells) ,cell=self.grid.all_cells.cells
        )

        for agent in agents:
            agent.team_arrangement(TEAM_ARRANGEMENT,TEAMS_FROM_THE_BEGINNING)

        self.running = True
        self.stabilization_time = 20 #for asserting when the simulation stabilizes
        
    
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


    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()

    
    def decrement_stabilization_time(self):
        self.stabilization_time -= 1
   
    def reset_stabilization_time(self):
        self.stabilization_time = 20


    def n_possible_coalitions(self):
        return 1
    
    def static_coalitions(self):
        #Coalitions are assigned after preparation's phase
        return False
    
    def preparation_condition(self):
        self.decrement_stabilization_time()
        res = False
        if self.stabilization_time == 0:
            self.reset_stabilization_time()
            res = True
        return res
    
    
    def termination_condition(self):
        
        self.decrement_stabilization_time()
        res = False
        if self.stabilization_time == 0:
            self.reset_stabilization_time()
            res = True
        return res
    
    def coalitions_formation(self,config=0):
        for agent in self.agents:
            agent.team_assign()
    
    def player_knockout(self,agentID):
        self.agents[agentID - 1].change_vote()

    def knockout_IDs(self):
        #They consider at least one example for each neighbourhood type
        agents_IDs = [548,281,318,583,589,438]
        return agents_IDs
        
    def payoff(self):
        #
        res = 0
        for agent in self.agents:
            if agent.vote == 1:
                res += 1

        return res
    def print_info(self,agentId):
        return ""