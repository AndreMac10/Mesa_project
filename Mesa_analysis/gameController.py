
from cooperativeExtension import cooperativeExtension

class GameController():
    
    def __init__(self, game_model:cooperativeExtension):
        self.model_class = game_model
        self.model = None
        self.knockedOutIDs = []
        self.marginal_contributions = []

        # (AGENT_ID, SHAPLEY_VALUE)
        self.shapley_values = []
        self.reference_payoff = []

    def run(self,fixed_config=False,config=0,parameters={}):
        #Based on how many coalitions are possible it should iterate
        #so that the results are used for computing the shapley value
        self.__reset()
        self.__simulate(parameters,config=config)
        if self.model.static_coalitions() and not fixed_config:
            for i in range(1,self.model.n_possible_coalitions()):
                self.__simulate(config=i)

        self.__compute_shapley_value()
        self.__print_results()
        return (self.marginal_contributions, self.shapley_values)
        #restituire i dati contributi marginali shapley value e l'agente
        

    def __simulate(self, parameters, config):
        #Runs 1 simulation for every knockedout player
        #and compute their contribute
        
        
        #Instantiation of the model
        self.model = self.model_class(**parameters)
        #Coalition formation before preparation phase
        if self.model.static_coalitions():
            self.model.coalitions_formation(config)
            
        #Preparation phase
        while(not self.model.preparation_condition()):
            self.model.step()
        print("SEED:",self.model._seed," PREP_STEP:",self.model.steps)
        #Coalition formation after preparation phase
        if not self.model.static_coalitions():
            self.model.coalitions_formation()
            
        #Copy of the simulation to use as a starting point
        model_ready = self.model.copy()
        

        #Running the unmodified simulation until the termination point
        while (not self.model.termination_condition()):
            self.model.step()
        print("END_REF:",self.model.steps)
        #Payoff of the unmodified simulation
        reference_payoff = self.model.payoff()
        self.reference_payoff.append(reference_payoff)
        

        #Generates the list of agents' IDs that will be knocked-out
        self.knockedOutIDs = model_ready.knockout_IDs()
        
        #Will hold the marginal contribution for each KOd agent    
        marg_contrib = []

        #Runs k different simulations each one with a different knocked out player
        for i in range(len(self.knockedOutIDs)):
            simulation = model_ready.copy()

            simulation.player_knockout(self.knockedOutIDs[i])

            while (not simulation.termination_condition()):
                simulation.step()

            #payoffs_KOd[i] = simulation.payoff()
            marg_contrib.append(reference_payoff - simulation.payoff())
            
            
        
        self.marginal_contributions.append(marg_contrib)
        

    def __compute_shapley_value(self):
        n = len(self.marginal_contributions)
        for i in range(len(self.knockedOutIDs)):
            sum = 0
            for contribs in self.marginal_contributions:
                sum += contribs[i]
            self.shapley_values.append((self.knockedOutIDs[i],sum / n))
        self.shapley_values.sort(key=lambda x: x[1],reverse=True)
        

    def __print_results(self):
        for line in self.shapley_values:
            print(f"Agent ID: {line[0]}  Shapley_value: {line[1]:.2f} {self.model.print_info(line[0])}")

    def __reset(self):
        self.knockedOutIDs = []
        self.marginal_contributions = []
        self.shapley_values = []





