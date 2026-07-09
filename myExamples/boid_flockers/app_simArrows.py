import os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

from matplotlib.markers import MarkerStyle

from model_simdbscan import BoidFlockers, BoidsScenario
from mesa.visualization import Slider, SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
import solara


GRID_SIZE = 50
N_BOIDS = 20
SEED = 113

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

# Global reactive state
selected_id = solara.reactive(None)

def boid_draw(agent):
    neighbors = len(agent.neighbors)
    deg = agent.angle
    rounded_deg = round(deg / 10) * 10 % 360

    # Highlight selected agent
    if agent.unique_id == selected_id.value:
        color = "blue"
    # elif neighbors >= 2:
    #     color = "green"
    else:
        color = "red"

    return AgentPortrayalStyle(
        color=color,
        size=20,
        marker=MARKER_CACHE[rounded_deg]
    )

@solara.component
def AgentSelector(model):
    agents = model.agents  # or model.schedule.agents depending on Mesa version

    def on_select(uid):
        selected_id.value = uid if selected_id.value != uid else None
        print(uid)

    def on_delete():
        if selected_id.value is not None:
            agent = next((a for a in agents if a.unique_id == selected_id.value), None)
            if agent:
                print(agent.unique_id)
                agent.remove()
            selected_id.value = None

    with solara.Card(title="Boid Inspector"):
        with solara.Column():
            for agent in agents:
                uid = agent.unique_id
                is_selected = selected_id.value == uid
                solara.Button(
                    label=f"{'★ ' if is_selected else ''}Boid {uid}",
                    on_click=lambda u=uid: on_select(u),
                    color="yellow" if is_selected else "default",
                )
            solara.Button(
                label="🗑 Delete Selected",
                on_click=on_delete,
                disabled=selected_id.value is None,
                color="error",
            )

model_params = {}
{
    "population_size": Slider(
        label="Number of boids",
        value=N_BOIDS,
        min=10,
        max=200,
        step=10,
    ),
    "rng" : SEED,
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
        (cluster_counter_view, 0),
        (AgentSelector, 0),         # <-- add this
    ],
    name="Boid Flocking Model with DBSCAN",
)
page  # noqa
