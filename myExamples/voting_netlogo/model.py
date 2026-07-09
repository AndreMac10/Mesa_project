import typing

import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

import mesa
from mesa.discrete_space import OrthogonalMooreGrid
from agents import VotingAgent

N_ROWS_COLUMNS = 30

# Per formare i team in base alla configurazione di partenza data da TEAM_ARRANGEMENT
TEAMS_FROM_THE_BEGINNING = False

TEAM_ARRANGEMENT = 3
#0  Head to Head
#1  Checker board
#2  Alternated Columns
#3  Random

class VotingGrid(mesa.Model):


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

        self.activation_order = activation_order
        self.grid = OrthogonalMooreGrid((size, size), torus=True, random=self.random)
        

        agents = VotingAgent.create_agents(
            self, len(self.grid.all_cells.cells) ,cell=self.grid.all_cells.cells
        )

        for agent in agents:
            agent.team_arrangement(TEAM_ARRANGEMENT,TEAMS_FROM_THE_BEGINNING)

        self.running = True
        
    
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