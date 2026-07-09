import os


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

from model import VotingGrid
from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle

def voting_agent_portrayal(agent):
    """
    Portrayal function for rendering Voting agents in the visualization.
    """
    return AgentPortrayalStyle(
        color="green" if agent.vote == 0 else "blue",
        marker = "o",
        size= 25
    )

# Model parameters
model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "size": {
        "type": "InputText",
        "value": 30,
        "label": "Grid Width and Height",
    },
    "activation_order": {
        "type": "Select",
        "value": "Random",
        "values": VotingGrid.activation_regimes,
        "label": "Activation Regime",
    },
}

# Initialize model
initial_model = VotingGrid()
# Create grid and agent visualization component using Altair
renderer = (
    SpaceRenderer(initial_model, backend="altair")
    .setup_agents(voting_agent_portrayal)
    .render()
)

# Create visualization with all components
page = SolaraViz(
    model=initial_model,
    renderer=renderer,
    model_params=model_params,
    name="Voting from NetLogo",
)
page  # noqa B018