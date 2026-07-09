import typing

import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

import mesa
from mesa.discrete_space import OrthogonalMooreGrid
from agents import PDAgent

N_ROWS_COLUMNS = 30
SEED = 116




TEAM_ARRANGEMENTS = {
    "Head to Head": 0,
    "Checker board": 1,
    "Alternated columns": 2,
    "Random" : 3,
    "Head to Head alternated borders" : 4,
}

class PdGrid(mesa.Model):
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


    def __init__(
        self, size=N_ROWS_COLUMNS, activation_order="Random", rng=SEED,
            grid_arrangement = "Head to Head"
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
        # try:
        #     clean_rng = int(rng) if rng is not None else 42
        # except (ValueError, TypeError):
        #     clean_rng = 42
            
        # Pass the cleaned integer to Mesa's Model class
        super().__init__(rng=rng)

        self.activation_order = activation_order
        self.grid = OrthogonalMooreGrid((size, size), torus=True, random=self.random)
        self.teamA = 0
        self.teamB = 0
        self.teamA_score = 0
        self.teamB_score = 0
        self.teamA_score_last = 0
        self.teamB_score_last = 0



        agents = PDAgent.create_agents(
            self, len(self.grid.all_cells.cells) ,cell=self.grid.all_cells.cells
        )
        #ATTENZIONE QUI SE NON VUOI FISSARE
        agents[461 - 1].change_strategy("Balanced")
        for agent in agents:
            team = agent.team_arrangement(TEAM_ARRANGEMENTS[grid_arrangement])
            if team == "A":
                self.teamA += 1
            else:
                self.teamB += 1



        self.datacollector = mesa.DataCollector(
            {
                "Cooperating_Agents": lambda m: len(
                    [a for a in m.agents if a.move == "C"]
                )
            }
        )

        self.running = True
        self.datacollector.collect(self)

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
    

    