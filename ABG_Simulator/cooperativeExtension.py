from abc import ABC, abstractmethod
import copy
from typing import Self


class cooperativeExtension(ABC):

    
    @abstractmethod
    def n_possible_coalitions(self) -> int:
        #returns the number of possible coalitions for the main team
        #relevant just if static coalitions is True
        #Should be 1 if static coalitions is False
        pass

    @abstractmethod
    def static_coalitions(self) -> bool:
        #returns True if teams are decided before the preparation's phase
        #returns False if teams are decided after the preparation's phase
        pass
    
    @abstractmethod
    def preparation_condition(self) -> bool:
        #Used by the controller to know when the preparation phase has been completed
        pass
    
    @abstractmethod
    def termination_condition(self) -> bool:
        #Used by the controller to know when the simulation has reached
        # a "stable" phase
        pass
    
    @abstractmethod
    def coalitions_formation(self, config:int) -> None:
        #assigns each agent to a team
        pass
    
    @abstractmethod
    def player_knockout(self, agent_id: int) -> None:
        #changes the behaviour of the agent "disabling" it
        #it can be deleted, change its team or use a default behaviour
        pass

    @abstractmethod
    def knockout_IDs(self)-> list[int]:
        #returns a list of agent IDs to be knocked out 
        #1 per each different simulation
        #They have to be from the main coalition
        pass
    
    @abstractmethod
    def payoff(self) -> int:
        #measurement of agents' behaviour
        #if team dependent should be computed from the main coalition perspective
        pass
    
    @abstractmethod
    def print_info(self,agentId:int) -> str:
        #additional information of the agent for printing results
        pass
    
    def copy(self) -> Self:
        return copy.deepcopy(self)
