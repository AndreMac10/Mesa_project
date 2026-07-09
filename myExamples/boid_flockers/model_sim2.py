"""
Boids Flocking Model
===================
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
"""

import os
import sys

# 1. Diciamo a Python dove si trova la radice del progetto (Mesa_project)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. IMPORT ASSOLUTI (Risolve l'errore del punto iniziale)
from myExamples.boid_flockers.agents import Boid
from Mesa_analysis.cooperativeExtension import cooperativeExtension

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)
SEED = 113
KO_AGENT = 13
SIM_SEED = 176
GRID_SIZE = 50
N_BOIDS = 20
EPS = 2.0
STABILIZATION_TIME = 100
STARTING_COALITIONS = 5



import numpy as np
import random
from mesa import DataCollector
from sklearn.cluster import DBSCAN
from collections import defaultdict

from mesa import Model
from mesa.experimental.continuous_space import ContinuousSpace
from mesa.experimental.scenarios import Scenario



class BoidsScenario(Scenario):
    """Scenario parameters for the Boids Flocking model.

    Args:
        population_size: Number of Boids in the simulation (default: 100)
        width: Width of the space (default: 100)
        height: Height of the space (default: 100)
        speed: How fast the Boids move (default: 1)
        vision: How far each Boid can see (default: 10)
        separation: Minimum distance between Boids (default: 2)
        cohere: Weight of cohesion behavior (default: 0.03)
        separate: Weight of separation behavior (default: 0.015)
        match: Weight of alignment behavior (default: 0.05)
        rng: Random rng for reproducibility (default: None)
    """

    population_size: int = N_BOIDS
    width: int = GRID_SIZE 
    height: int = GRID_SIZE 
    speed: float = 1.0
    vision: float = 10.0
    separation: float = 2.0
    cohere: float = 0.03
    separate: float = 0.015
    match: float = 0.05

class BoidFlockers(Model, cooperativeExtension):
    """Flocker model class. Handles agent creation, placement and scheduling."""

    def __init__(self, sim_seed = SIM_SEED, scenario=None, rng=SEED, ko_agent = KO_AGENT):
        """Create a new Boids Flocking model.

        Args:
            scenario: BoidsScenario object containing model parameters.
        """
        if scenario is None:
            scenario = BoidsScenario(rng=rng)  # fresh seed every instantiation

        elif scenario.rng is None:
            scenario.rng = rng
            

        super().__init__(scenario=scenario)

        self.agent_angles = np.zeros(
            scenario.population_size
        )  # holds the angle representing the direction of all agents at a given step

        # Set up for dbscan
        self.eps = EPS
        self.min_samples = 2
        self.cluster_count = 0
        self.stabilization_time = STABILIZATION_TIME
        self.coalitions = []
        self.payoff_data = []
        self.random = random.Random(sim_seed)
        self.ready = False
        self.ko_agent = ko_agent
        
        self.datacollector = DataCollector(
            model_reporters={"Cluster Count": lambda m: m.cluster_count}
        )
        
        # Set up the space
        self.space = ContinuousSpace(
            [[0, scenario.width], [0, scenario.height]],
            torus=True,
            random=self.random,
            n_agents=scenario.population_size,
        )

        # Create and place the Boid agents
        positions = (
            self.rng.random(size=(scenario.population_size, 2)) * self.space.size
        )
        directions = self.rng.uniform(-1, 1, size=(scenario.population_size, 2))
        Boid.create_agents(
            self,
            scenario.population_size,
            self.space,
            position=positions,
            direction=directions,
            cohere=scenario.cohere,
            separate=scenario.separate,
            match=scenario.match,
            speed=scenario.speed,
            vision=scenario.vision,
            separation=scenario.separation,
        )

        # For tracking statistics
        self.average_heading = None
        self.update_average_heading()

    # vectorizing the calculation of angles for all agents
    def calculate_angles(self):
        d1 = np.array([agent.direction[0] for agent in self.agents])
        d2 = np.array([agent.direction[1] for agent in self.agents])
        self.agent_angles = np.degrees(np.arctan2(d1, d2))
        for agent, angle in zip(self.agents, self.agent_angles):
            agent.angle = angle

    def update_average_heading(self):
        """Calculate the average heading (direction) of all Boids."""
        if not self.agents:
            self.average_heading = 0
            return

        headings = np.array([agent.direction for agent in self.agents])
        mean_heading = np.mean(headings, axis=0)
        self.average_heading = np.arctan2(mean_heading[1], mean_heading[0])

    def find_clusters(self):
         # 1. Extract Positions (x, y) and Headings (dx, dy)
        agents_list = list(self.agents)
        data = [[*a.position, *a.direction] for a in agents_list]
        # 2. Run DBSCAN
        if len(data) > 0:
            db = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(np.array(data))
            # 3. Count clusters (exclude noise label -1)
            labels = db.labels_
            self.cluster_count = len(set(labels)) - (1 if -1 in labels else 0)
            if self.cluster_count == STARTING_COALITIONS: self.ready = True


    def step(self):
        """Run one step of the model.

        All agents are activated in random order using the AgentSet shuffle_do method.
        """
        if self.ready:
            self.shuffled_step()
        else:
            self.agents.shuffle_do("step")
        self.update_average_heading()
        self.calculate_angles()

        self.find_clusters()
        #print(self.cluster_count, self.steps)
        
        
        self.datacollector.collect(self)

    def n_possible_coalitions(self):
        return 1
    
    def static_coalitions(self):
        #Coalitions are assigned after preparation's phase
        return False
    
    def preparation_condition(self):
        cond = False
        if self.cluster_count < STARTING_COALITIONS:
            pass
        else:
            cond = True
            self.ready = True
        return cond
        #return self.is_stable()
    
    def decrement_stabilization_time(self):
        self.stabilization_time -= 1
   
    def reset_stabilization_time(self):
        self.stabilization_time = STABILIZATION_TIME
    
    def is_stable(self):
        self.decrement_stabilization_time()
        res = False
        if self.stabilization_time == 0:
            self.reset_stabilization_time()
            res = True
        return res
    
    def termination_condition(self):
        return self.is_stable()
    
    def coalitions_formation(self,config=0):
        #run dbscan and assign to each agent its team (cluster)
        # 1. Extract Positions (x, y) and Headings (dx, dy)
        agents_list = list(self.agents)
        data = [[*a.position, *a.direction] for a in agents_list]
        # 2. Run DBSCAN
        if len(data) > 0:
            db = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(np.array(data))
            # 3. Count clusters (exclude noise label -1)
            clusters_dict = defaultdict(list)
            for agent, label in zip(agents_list, db.labels_):
                agent.clusterID = label
                if label == -1:
                    continue
                clusters_dict[label].append(agent.unique_id)
            #print(clusters_dict)
            self.coalitions = [clusters_dict[k] for k in clusters_dict.keys() ]
        

    
    def player_knockout(self,agentID):
        #print(agentID)
        self.agents[agentID - 1].remove()
    
    def knockout_IDs(self):
        agents_IDs = self.coalitions[0]
        agents_IDs = [self.ko_agent]
        #print(agents_IDs)
        #scelta una coalizione prende l'ID di tutti i boids
        #o una buona parte
        return agents_IDs

    

    def payoff(self):
        agents_list = list(self.agents)
        if not agents_list:
            return 0.0

        # Estrazione dati (posizione + direzione)
        data = np.array([[*a.position, *a.direction] for a in agents_list])

        # Clustering con DBSCAN
        db = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(data)
        labels = db.labels_
        
        # Maschera per i core points (punti densi)
        core_mask = np.zeros(len(agents_list), dtype=bool)
        core_mask[db.core_sample_indices_] = True

        # Conteggi principali
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_outliers = np.sum(labels == -1)
        total_agents = len(agents_list)

        # Condizione di guardia: se DBSCAN trova solo rumore
        if n_clusters == 0:
            return 0.0

        # --- 1. MINIMIZZARE OUTLIER (Peso: 0.6) ---
        # Più è vicino a 1, meno outlier ci sono (1 = zero outlier)
        outlier_score = 1.0 - (n_outliers / total_agents)

        # --- 2. MINIMIZZARE NUMERO DI CLUSTER (Peso: 0.3) ---
        # 1 cluster = 1.0 (ottimo), più aumentano più tende a 0
        cluster_score = 1.0 / n_clusters

        # --- 3. MASSIMIZZARE DENSITÀ INTRA-CLUSTER (Peso: 0.1) ---
        # Rapporto tra core points e punti totali del cluster
        density_scores = []
        for cluster_id in set(labels):
            if cluster_id == -1:
                continue
            cluster_indices = np.where(labels == cluster_id)[0]
            n_cores = np.sum(core_mask[cluster_indices])
            density_scores.append(n_cores / len(cluster_indices))
        
        density_score = np.mean(density_scores) if density_scores else 0.0

        # --- NUOVI PESI RICHIESTI ---
        w_outlier = 0.6
        w_cluster = 0.3
        w_density = 0.1

        # Calcolo payoff combinato (Resta rigidamente tra 0.0 e 1.0)
        payoff_val = (w_outlier * outlier_score) + (w_cluster * cluster_score) + (w_density * density_score)

        # Opzionale: moltiplica per 100 per averlo in scala 0-100 (es. 85.5 invece di 0.855)
        return payoff_val * 100
    
    def print_info(self,agentId):
        res = ""
        #res = "Clusters: {} Density: {} Outliers: {}".format(self.payoff_data[0], self.payoff_data[1], self.payoff_data[2])
        return res

    def shuffled_step(self):
        # da copiare non usare direttamente

        agents = list(self.agents)
        self.random.shuffle(agents)

        for agent in agents:
            if agent in self.agents:
                agent.step()