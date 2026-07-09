import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

from matplotlib.markers import MarkerStyle

from model import BoidFlockers, BoidsScenario
from mesa.visualization import Slider, SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
import solara


GRID_SIZE = 50
N_BOIDS = 10

# Pre-compute markers for different angles (e.g., every 10 degrees)
MARKER_CACHE = {}
for angle in range(0, 360, 10):
    marker = MarkerStyle(10)
    marker._transform = marker.get_transform().rotate_deg(angle)
    MARKER_CACHE[angle] = marker

# 1. Define a custom Solara component to display the counter
def cluster_counter_view(model):
    """A simple component to display the live cluster count."""
    return solara.Card(
        title="Clustering Metrics",
        children=[
            solara.Markdown(f"### Current Clusters: **{model.cluster_count}**"),
            solara.Text(f"Grouping based on Position + Direction")
        ]
    )

def boid_draw(agent):
    neighbors = len(agent.neighbors)

    # Calculate the angle
    deg = agent.angle
    # Round to nearest 10 degrees
    rounded_deg = round(deg / 10) * 10 % 360

    # using cached markers to speed things up
    boid_style = AgentPortrayalStyle(
        color="red", size=20, marker=MARKER_CACHE[rounded_deg]
    )
    if neighbors >= 2:
        boid_style.update(("color", "green"), ("marker", MARKER_CACHE[rounded_deg]))
    return boid_style


model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "population_size": Slider(
        label="Number of boids",
        value=N_BOIDS,
        min=10,
        max=200,
        step=10,
    ),
    "width": GRID_SIZE,
    "height": GRID_SIZE,
    "speed": Slider(
        label="Speed of Boids",
        value=5,
        min=1,
        max=20,
        step=1,
    ),
    "vision": Slider(
        label="Vision of Bird (radius)",
        value=10,
        min=1,
        max=50,
        step=1,
    ),
    "separation": Slider(
        label="Minimum Separation",
        value=2,
        min=1,
        max=20,
        step=1,
    ),
}

model = BoidFlockers(scenario=BoidsScenario())

# Quickest way to visualize grid along with agents or property layers.
renderer = (
    SpaceRenderer(
        model,
        backend="matplotlib",
    )
    .setup_agents(boid_draw)
    .render()
)

page = SolaraViz(
    model,
    renderer,
    model_params=model_params,
    components=[
        (cluster_counter_view, 0), # Display on page 0 (main page)
        #make_plot_component("Cluster Count") # History plot from DataCollector
    ],
    name="Boid Flocking Model with DBSCAN",
)
page  # noqa
