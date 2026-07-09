from mesa.discrete_space import CellAgent

N_ROWS_COLUMNS = 30
CHANGE_VOTE_IF_TIED = False
AWARD_CLOSE_CALLS_TO_LOSER = False

class VotingAgent(CellAgent):
    """" Voter in the voting problem in Social Science """

    def __init__(self, model, cell=None):
        """Create a new VoterAgent"""

        super().__init__(model)

        self.team = -1
        self.cell = cell
        self.nextVote = None
        self.team_assigned = False

    
    def step(self):
        """ Evaluates neighbors' votes and follows the majority"""
        
        neighbors = list(self.cell.neighborhood.agents)
        votes = 0

        for neighbor in neighbors:
            if(neighbor==self): continue
            votes = votes + neighbor.vote
        
        if(CHANGE_VOTE_IF_TIED):
            if votes == 4: self.change_vote()
        if(AWARD_CLOSE_CALLS_TO_LOSER):
            if votes == 5 and self.vote == 1: self.change_vote()
            elif votes == 3 and self.vote == 0: self.change_vote()
        if votes > 4 and self.vote == 0: self.change_vote()
        elif votes < 4 and self.vote == 1: self.change_vote()
    
    def change_vote(self):
        self.nextVote = 0 if self.vote == 1 else 1



    def advance(self):
        if self.nextVote is not None:
            self.vote = self.nextVote

    def team_assign(self):
        if not self.team_assigned:
            self.team = 1 if self.vote else 0
            self.team_assigned = True
    
    def team_remove(self):
        self.team = -1
        self.team_assigned = False

    def team_arrangement(self, arrangementType, teams_from_the_beginning):
        
        #team selection
        match arrangementType:
            case 0:
                self.head_to_head_arrangement()
            case 1:
                self.checker_arrangement()
            case 2:
                self.alternated_columns_arrangement()
            case 3:
                self.vote = self.random.choice([0, 1])
            case _:
                print("DEBUG: Nessun match trovato!")
        if teams_from_the_beginning:
            self.team = 1 if self.vote else 0

    

    def head_to_head_arrangement(self):
        half_size = N_ROWS_COLUMNS / 2 
        self.vote = 0 if self.cell.position[0] < half_size else 1

    def alternated_columns_arrangement(self):
        self.vote = 0 if self.cell.position[0] % 2 != 1 else 1

    def checker_arrangement(self):
        x = self.cell.position[0]
        y = self.cell.position[1]
        match x % 2:
            case 0:
                self.vote = 1 if y % 2 else 0
            case 1:
                self.vote = 0 if y % 2 else 1



