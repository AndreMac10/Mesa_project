
import numpy as np

from mesa.discrete_space import CellAgent

N_ROWS_COLUMNS = 30

STRATEGIES = {
    "Balanced": (0.33,0.33,0.33),
    "Selfish" : (1,0,0),
    "TeamDevote": (0,1,0),
    "OpponentHater" : (0,0,1),
}

FROMSTRATEGIES = {
    (0.33,0.33,0.33) : "Balanced",
    (1,0,0) : "Selfish",
    (0,1,0) : "TeamDevote",
    (0,0,1) : "OpponentHater",
}
STARTING_MOVE = {
    "Balanced" : "C",
    "Selfish" : "D",
    "TeamDevote" : "C",
    "OpponentHater" : "D",

}



class PDAgent(CellAgent):
    """Agent member of the iterated, spatial prisoner's dilemma model."""

    def __init__(self, model,cell=None ):
        """
        Create a new Prisoner's Dilemma agent.

        Args:
            model: model instance
            starting_move: If provided, determines the agent's initial state:
                           C(ooperating) or D(efecting). Otherwise, random.
        """
        super().__init__(model)
        self.score = 0
        self.cell = cell
        self.behaviour = STRATEGIES[self.random.choice(list(STRATEGIES.keys()))]
        #self.behaviour = self.random.choice(self.strategies)
        #self.behaviour = (0.5,0,0.5)
        #
        self.move = STARTING_MOVE[FROMSTRATEGIES[self.behaviour]]
        self.next_move = None

    def team_arrangement(self, arrangementType):
        
        #team selection
        match arrangementType:
            case 0:
                self.head_to_head_arrangement()
            case 1:
                self.checker_arrangement()
            case 2:
                self.alternated_columns_arrangement()
            case 3:
                self.team = self.random.choice(["A","B"])
            case 4:
                None
                #self.team = self.head_to_head_alternated_borders()
            case _:
                print("DEBUG: Nessun match trovato!")
        return self.team

            
    


        

        

    @property
    def is_cooroperating(self):
        return self.move == "C"
    
    def step(self):

        neighbors = self.cell.neighborhood.agents
        opp_team = self.other_team()
        n_teammates = 0
        n_opponents = 0
        teammates_C = 0
        opponents_C = 0
        teammates_D = 0
        opponents_D = 0        
        for neighbor in neighbors:
            
            match [neighbor.team,neighbor.move]:

                case [self.team, "C"]:
                    n_teammates += 1
                    teammates_C += 1
                case [self.team, "D"]:
                    n_teammates += 1
                    teammates_D += 1
                case[opp_team, "C"]:
                    n_opponents += 1
                    opponents_C += 1
                case[opp_team, "D"]:
                    n_opponents += 1
                    opponents_D += 1

        assert(n_teammates + n_opponents == 8)
        assert(teammates_C + teammates_D == n_teammates)
        assert(opponents_C + opponents_D == n_opponents)
        self.next_move = self.choose_move(n_teammates, teammates_C, opponents_C, self.behaviour)



    def choose_move(self, n_alleati_totali, alleati_cooperanti, rivali_cooperanti, pesi ):
        n_rivali_totali = 8 - n_alleati_totali
        alleati_che_tradiscono = n_alleati_totali - alleati_cooperanti
        rivali_che_tradiscono = n_rivali_totali - rivali_cooperanti

        
        # alfa -> Importanza del mio punteggio
        alfa = pesi[0]
        # beta -> Importanza del punteggio dei miei compagni
        beta = pesi[1]
        # gamma -> Cattiveria verso i rivali (puniti se questo peso è alto)
        gamma = pesi[2]

        #Ipotesi "C"

        # 1a. Mio payoff personale
        mio_payoff_se_C = (alleati_cooperanti * 1.0) + (alleati_che_tradiscono * 0.5) + (rivali_cooperanti * -0.8)
        
        # 1b. Punti che REGALO ai miei alleati se io faccio C 
        # Gli alleati che fanno C con me fanno un punto (C,C -> 1). Chi fa D contro il mio C fa 0.5 (D,C -> 0.5)
        punti_regalati_alleati_se_C = (alleati_cooperanti * 1.0) + (alleati_che_tradiscono * 0.5)
        
        # 1c. Punti che CONCEDO ai rivali se io faccio C 
        # Il rivale che fa C contro il mio C fa -0.8. Il rivale che fa D contro il mio C fa +1.6
        punti_concessi_rivali_se_C = (rivali_cooperanti * -0.8) + (rivali_che_tradiscono * 1.6)

        # Utilità totale netta dello scenario C
        utilita_C = (alfa * mio_payoff_se_C) + (beta * punti_regalati_alleati_se_C) - (gamma * punti_concessi_rivali_se_C)


        #Ipotesi D

        # 2a. Mio payoff personale
        mio_payoff_se_D = (alleati_cooperanti * -1.0) + (rivali_cooperanti * 1.6)
        
        # 2b. Punti che REGALO ai miei alleati se io faccio D
        # Se io faccio D, l'alleato che ha fatto C subisce -1.0. L'alleato che ha fatto D subisce 0
        punti_regalati_alleati_se_D = (alleati_cooperanti * -1.0) + (alleati_che_tradiscono * 0.0)
        
        # 2c. Punti che CONCEDO ai rivali se io faccio D
        # Se io faccio D, il rivale che ha fatto C subisce 0. Il rivale che ha fatto D subisce 0
        punti_concessi_rivali_se_D = (rivali_cooperanti * 0.0) + (rivali_che_tradiscono * 0.0)

        # Utilità totale netta dello scenario D
        utilita_D = (alfa * mio_payoff_se_D) + (beta * punti_regalati_alleati_se_D) - (gamma * punti_concessi_rivali_se_D)


        # =========================================================================
        # DECISIONE FINALE
        # =========================================================================
        return "C" if utilita_C > utilita_D else "D"





    def advance(self):
        self.move = self.next_move
        #self.player._history._plays.append(self.move)
        self.score = self.increment_score()

    def increment_score(self):
        neighbors = self.cell.neighborhood.agents
        moves = []
        teams = []
        sum = 0.0
        if self.model.activation_order == "Simultaneous":
            for neighbor in neighbors:
                moves.append(neighbor.next_move)
                teams.append(neighbor.team)
        else:
            for neighbor in neighbors:
                moves.append(neighbor.move)
                teams.append(neighbor.team)
        
        for i in range(len(moves)):
            sum = sum + self.model.score((self.move,moves[i]),self.team,teams[i])
        
        self.model.add_score(self,sum)
        return sum
    
    def personal_score(self):
        neighbors = self.cell.neighborhood.agents
        moves = []
        teams = []
        sum = 0.0
        if self.model.activation_order == "Simultaneous":
            for neighbor in neighbors:
                moves.append(neighbor.next_move)
                teams.append(neighbor.team)
        else:
            for neighbor in neighbors:
                moves.append(neighbor.move)
                teams.append(neighbor.team)
        
        for i in range(len(moves)):
            sum = sum + self.model.score((self.move,moves[i]),self.team,teams[i])
        
        return sum

    
   
    def head_to_head_arrangement(self):
        half_size = N_ROWS_COLUMNS / 2 
        self.team = "A" if self.cell.position[0] < half_size else "B"
    
    
    def alternated_columns_arrangement(self):
        self.team = "A" if self.cell.position[0] % 2 != 1 else "B"

    def checker_arrangement(self):
        x = self.cell.position[0]
        y = self.cell.position[1]
        match x % 2:
            case 0:
                self.team = "B" if y % 2 else "A"
            case 1:
                self.team = "A" if y % 2 else "B"
    
    def knockout(self):
        #Always defects
        self.behaviour = (0,0,0)

    def neighbors_info(self):
        neighbors = self.cell.neighborhood.agents
        print("Team target_agent",self.unique_id,":",self.team,"Strategy:",self.strategy_name())
        for neighbor in neighbors:
            if(neighbor.unique_id == self.unique_id): continue
            print(neighbor.strategy_name(), neighbor.team, neighbor.unique_id)
        
    def strategy_name(self):
        return FROMSTRATEGIES[self.behaviour]
    
    def other_team(self):
        team = "B" if self.team == "A" else "A"
        return team
    
    def change_strategy(self, strategy):
        self.behaviour = STRATEGIES[strategy]
        self.move = STARTING_MOVE[FROMSTRATEGIES[self.behaviour]]

        


