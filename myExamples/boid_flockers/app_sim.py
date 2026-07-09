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
SEED = 149

# Pre-compute markers for different angles (e.g., every 10 degrees)
import matplotlib.path as mpath

# 1. Definiamo i vertici (X, Y) e i comandi di tracciamento di una freccia
arrow_verts = [
    (-0.15, -0.5),  # Base sinistra della coda
    (-0.15,  0.1),  # Angolo interno sinistro
    (-0.5,   0.1),  # Esterno sinistro della punta
    ( 0.0,   0.6),  # Punta centrale
    ( 0.5,   0.1),  # Esterno destro della punta
    ( 0.15,  0.1),  # Angolo interno destro
    ( 0.15, -0.5),  # Base destra della coda
    (-0.15, -0.5)   # Chiusura poligono (ritorno all'origine)
]
arrow_codes = [
    mpath.Path.MOVETO,
    mpath.Path.LINETO,
    mpath.Path.LINETO,
    mpath.Path.LINETO,
    mpath.Path.LINETO,
    mpath.Path.LINETO,
    mpath.Path.LINETO,
    mpath.Path.CLOSEPOLY,
]
# Creiamo il Path SVG nativo
arrow_path = mpath.Path(arrow_verts, arrow_codes)

# 2. Inseriamo la nostra freccia nella Cache pre-ruotata
MARKER_CACHE = {}
for angle in range(0, 360, 10):
    marker = MarkerStyle(arrow_path)
    
    # Applichiamo la rotazione. 
    # NOTA: La nostra freccia di base punta verso l'ALTO.
    # Se in Mesa il tuo angolo 0 rappresenta la direzione verso DESTRA (Standard),
    # cambia la riga sotto in: marker.get_transform().rotate_deg(angle - 90)
    marker._transform = marker.get_transform().rotate_deg(angle + 180)
    
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

import matplotlib.colors as mcolors
import matplotlib.cm as cm
from mesa.visualization.components import AgentPortrayalStyle

# Pre-calcoliamo i colori per i cluster
cmap = cm.get_cmap('tab10')
CLUSTER_COLORS = [mcolors.to_hex(cmap(i)) for i in range(10)]

def boid_draw(agent):
    deg = agent.angle
    rounded_deg = round(deg / 10) * 10 % 360

    # 1. Default: Grigio e piccolo (Outlier / Rumore)
    color = "lightgray"
    size = 15

    # 2. Assegnazione colore in base al cluster_id puro calcolato da DBSCAN
    cluster_id = getattr(agent, 'cluster_id', -1) 
    if cluster_id != -1:
        color = CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
        size = 20

    # 3. Evidenzia l'agente selezionato
    if agent.unique_id == selected_id.value:
        color = "black"
        size = 35

    return AgentPortrayalStyle(
        color=color,
        size=size,
        marker=MARKER_CACHE[rounded_deg]
    )
# 1. Define a custom Solara component to display the counter
def cluster_counter_view(model):
    """A simple component to display the live cluster count."""
    
    # Usiamo getattr per sicurezza, nel caso la variabile non esista al primissimo tick
    outliers = getattr(model, 'outlier_count', 0)
    
    return solara.Card(
        title="Clustering Metrics",
        children=[
            solara.Markdown(f"### Current Clusters: **{model.cluster_count}**"),
            solara.Markdown(f"### Outliers: **{outliers}**"), # <-- Nuova riga
            solara.Text(f"Grouping based on Position + Direction")
        ]
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
