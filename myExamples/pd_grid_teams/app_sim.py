"""
Solara-based visualization for the Spatial Prisoner's Dilemma Model.
"""

import os
import solara
import altair as alt


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)

from model_interface_ready_sim2 import PdGrid1
from mesa.visualization import (
    Slider,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
    make_space_component,
)
from mesa.visualization.components import AgentPortrayalStyle



def pd_agent_portrayal(agent):
    return {
        "id": agent.unique_id,
        "color": "blue" if agent.move == "C" else "red",
        "marker": "square" if agent.team == "A" else "circle",
        "size": 15,
    }

TEAM_ARRANGEMENTS = {
    "Head to Head": 0,
    "Checker board": 1,
    "Alternated columns": 2,
    "Random" : 3,
    "Head to Head alternated borders" : 4,
}

SEED = 122
AGENT_ID = 671
STRATEGIES = [ "Balanced", "Selfish", "TeamDevote", "OpponentHater" ]
STRATEGY = STRATEGIES[0]

# 1. Create a reactive state to track what the user types in the input box
typed_agent_id = solara.reactive("")
selected_team_arrangement = solara.reactive("Head to Head")
chosen_arrangement = TEAM_ARRANGEMENTS[selected_team_arrangement.value]

#  CORRETTO
def payoff_squadre_dinamici(model):
    payoff_A = getattr(model, "teamA_score_last", 0)
    payoff_B = getattr(model, "teamB_score_last", 0)
    
    with solara.Card("Payoff di Squadra Corrente", subtitle=f"Turno: {model.steps}", elevation=3):
        with solara.Row(justify="space-around"):
            solara.Markdown(f"### **Squadra A:** {payoff_A:.2f}")
            solara.Markdown(f"### **Squadra B:** {payoff_B:.2f}")
        #solara.Markdown("**Stato:** " + ("A in vantaggio" if payoff_A > payoff_B else "B in vantaggio" if payoff_B > payoff_A else "Pareggio"))


@solara.component
def CustomLayoutWrapper(model):
    """
    This custom component renders your existing grid layout, 
    and places a text box card directly beneath it.
    """
    with solara.Card("Distribuzione Iniziale Squadre", elevation=2):
        with solara.Row(justify="space-around", style={"flex-wrap": "nowrap"}):
            solara.Markdown(
                f"**Squadra A:** {model.teamA} giocatori",
                style={"white-space": "nowrap"}
            )
            solara.Markdown(
                f"**Squadra B:** {model.teamB} giocatori",
                style={"white-space": "nowrap"}
            )
        # with solara.Row(justify="space-around", style={"flex-wrap": "nowrap"}):
        #     solara.Markdown(
        #         f"**Punteggio Squadra A:** {getattr(model,"teamA_score_last",0)}",
        #         style={"white-space": "nowrap"}
        #     )
        #     solara.Markdown(
        #         f"**Punteggio Squadra B:** {getattr(model,"teamB_score_last",0)}",
        #         style={"white-space": "nowrap"}
        #     )
    



    # Render the input controls right below the grid canvas
    with solara.Card("Manual Agent Team Editor", style="width: 400px; margin: 20px auto;"):
        
        # Text input field linked directly to our reactive variable
        solara.InputText(
            label="Enter Agent ID", 
            value=typed_agent_id,
            continuous_update=False  # Only updates the variable when they finish typing or press Enter
        )
        
        def modify_agent_by_id():
            target_id = int(typed_agent_id.value)
            print(f"Received: {target_id}")
            
            # Search Mesa's internal id container for the matching agent object
            target_agent = model.agents[target_id - 1]
            print(f"{target_agent}")
            if target_agent:
                print(f"Successfully executed knockout of agent ID: {target_id}")
                #target_agent.knockout()
                target_agent.neighbors_info()
            

        # Trigger button to fire the modification function
        solara.Button(
            label="Agent Knockout", 
            on_click=modify_agent_by_id, 
            color="primary",
            style="margin-top: 10px; width: 100%;"
        )


# Create plot for tracking cooperating agents over time
plot_component = make_plot_component("Cooperating_Agents", backend="altair", grid=True)

# Create grid and agent visualization component using Altair

def make_space(chart):
    return (
        chart
        .mark_point(opacity=0.8, filled=True, size=225)
        .encode(
            shape=alt.Shape(
                "marker:N",
                scale=alt.Scale(
                    domain=["square", "circle"],
                    range=["square", "circle"]
                ),
                legend=None
            ),
            tooltip=["id:N"]  # only show id on hover
        )
        .properties(width=600, height=600)
    )

grid_component = make_space_component(
    agent_portrayal=pd_agent_portrayal,
    backend="altair",
    post_process=make_space,
)

# Model parameters
model_params = {

    "fixed_agentID" : AGENT_ID, 
    "fixed_strategy" : STRATEGY,
    "rng": SEED,
}
{
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
        "values": PdGrid1.activation_regimes,
        "label": "Activation Regime",
    },
        "grid_arrangement": {
            "type": "Select",
            "value": "Head to Head",                            # integer values now
            "values": list(TEAM_ARRANGEMENTS.keys()),
            "label": "Team Arrangement",
    },
}






# Initialize model
initial_model = PdGrid1(**model_params)
# Create grid and agent visualization component using Altair

# Create visualization with all components
page = SolaraViz(
    model=initial_model,
    components=[
        grid_component, CustomLayoutWrapper, payoff_squadre_dinamici],
    model_params=model_params,
    name="Spatial Prisoner's Dilemma with teams",
)
page  # noqa B018
