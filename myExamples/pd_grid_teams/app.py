"""
Solara-based visualization for the Spatial Prisoner's Dilemma Model.
"""

import os


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

from model import PdGrid
from mesa.visualization import (
    Slider,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle


def pd_agent_portrayal(agent):
    """
    Portrayal function for rendering PD agents in the visualization.
    """
    return AgentPortrayalStyle(
        color="blue" if agent.move == "C" else "red",
        marker="s" if agent.team == "A" else "o",
        size=15
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
        "values": PdGrid.activation_regimes,
        "label": "Activation Regime",
    },
}


# Create plot for tracking cooperating agents over time
plot_component = make_plot_component("Cooperating_Agents", backend="altair", grid=True)

# Initialize model
initial_model = PdGrid()
# Create grid and agent visualization component using Altair
renderer = (
    SpaceRenderer(initial_model, backend="altair")
    .setup_agents(pd_agent_portrayal)
    .render()
)

# Create visualization with all components
page = SolaraViz(
    model=initial_model,
    renderer=renderer,
    components=[plot_component],
    model_params=model_params,
    name="Spatial Prisoner's Dilemma",
)
page  # noqa B018
