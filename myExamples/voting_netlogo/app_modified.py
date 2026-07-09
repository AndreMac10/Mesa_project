import os
import solara
import altair as alt

# Imposta la directory di lavoro
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from model_interface_ready_sim1 import VotingGrid1
from mesa.visualization import (
    SolaraViz,
    make_space_component,
)

# =========================================================================
# DATI SHAPLEY (ID: Valore)
# =========================================================================
shapley_data = {
    238: 7.00, 299: 7.00, 329: 7.00, 396: 6.00, 397: 6.00, 62: 5.00, 56: 4.00, 
    57: 4.00, 162: 4.00, 163: 4.00, 179: 4.00, 180: 4.00, 181: 4.00, 192: 4.00, 
    193: 4.00, 194: 4.00, 195: 4.00, 208: 4.00, 209: 4.00, 210: 4.00, 211: 4.00, 
    225: 4.00, 239: 4.00, 240: 4.00, 100: 3.00, 129: 3.00, 130: 3.00, 159: 3.00, 
    160: 3.00, 161: 3.00, 190: 3.00, 191: 3.00, 267: 3.00, 268: 3.00, 297: 3.00, 
    298: 3.00, 328: 3.00, 335: 3.00, 336: 3.00, 364: 3.00, 365: 3.00, 366: 3.00, 
    367: 3.00, 384: 3.00, 385: 3.00, 414: 3.00, 415: 3.00, 416: 3.00, 445: 3.00, 
    446: 3.00, 475: 3.00, 569: 3.00, 598: 3.00, 599: 3.00, 628: 3.00, 629: 3.00, 
    630: 3.00, 659: 3.00, 660: 3.00, 684: 3.00, 685: 3.00, 1: 2.00, 2: 2.00, 
    20: 2.00, 31: 2.00, 32: 2.00, 63: 2.00, 64: 2.00, 65: 2.00, 85: 2.00, 
    86: 2.00, 87: 2.00, 93: 2.00, 94: 2.00, 115: 2.00, 116: 2.00, 241: 2.00, 
    270: 2.00, 271: 2.00, 300: 2.00, 330: 2.00, 830: 2.00, 859: 2.00, 860: 2.00, 
    872: 2.00, 889: 2.00, 890: 2.00, 12: 1.00, 13: 1.00, 26: 1.00, 27: 1.00, 
    42: 1.00, 43: 1.00, 72: 1.00, 137: 1.00, 138: 1.00, 166: 1.00, 167: 1.00, 
    168: 1.00, 202: 1.00, 203: 1.00, 232: 1.00, 233: 1.00, 262: 1.00, 422: 1.00, 
    426: 1.00, 427: 1.00, 451: 1.00, 452: 1.00, 456: 1.00, 481: 1.00, 482: 1.00, 
    554: 1.00, 583: 1.00, 584: 1.00, 613: 1.00, 614: 1.00, 624: 1.00, 654: 1.00, 
    655: 1.00, 714: 1.00, 715: 1.00, 722: 1.00, 723: 1.00, 729: 1.00, 730: 1.00, 
    744: 1.00, 752: 1.00, 753: 1.00, 758: 1.00, 759: 1.00, 760: 1.00, 783: 1.00, 
    823: 1.00, 824: 1.00, 853: 1.00, 854: 1.00, 883: 1.00, 896: 1.00
}

# =========================================================================
# VARIABILI REATTIVE SOLARA
# =========================================================================
typed_agent_id = solara.reactive("")
use_vote_markers = solara.reactive(False)
show_heatmap = solara.reactive(False) 

# =========================================================================
# PORTRAYAL DINAMICO (Logica Unificata e Sequenziale)
# =========================================================================
def voting_agent_portrayal(agent):
    if use_vote_markers.value: 
        agent.team_assign()
    else:
        agent.team_remove()

    # 1. DETERMINAZIONE DELLA FORMA (Priorità al KO, poi alla forma congelata)
    is_ko = getattr(agent, "is_ko", False)
    if is_ko:
        marker = "diamond"  # Il Knockout vince sempre ed è un Diamante
    elif use_vote_markers.value:
        # Se la casella è attiva, congeliamo la forma basandoci sul voto CORRENTE.
        # Una volta salvata in 'fixed_marker', se l'agente cambia voto durante la simulazione,
        # la forma rimarrà comunque quella memorizzata.
        if not hasattr(agent, "fixed_marker"):
            agent.fixed_marker = "square" if int(agent.vote) == 1 else "circle"
        marker = agent.fixed_marker
    else:
        # Se disattivata, resettiamo la memoria e tornano tutti quadrati di partenza
        if hasattr(agent, "fixed_marker"):
            delattr(agent, "fixed_marker")
        marker = "square"

    # 2. DETERMINAZIONE DEL COLORE (Heatmap o Colore di Fazione)
    s_val = shapley_data.get(agent.unique_id, 0.0)
    
    if show_heatmap.value and agent.unique_id in shapley_data:
        heatmap_palette = {
            1.0: "#ffeb3b", # Giallo
            2.0: "#fbc02d", # Giallo scuro
            3.0: "#ffa000", # Arancione chiaro
            4.0: "#f57c00", # Arancione
            5.0: "#e65100", # Arancione scuro
            6.0: "#d84315", # Rosso aranciato
            7.0: "#b71c1c"  # Rosso scuro
        }
        color = heatmap_palette.get(s_val, "#ffeb3b")
    else:
        # Il colore continua a seguire dinamicamente il voto (Blu=1, Verde=0)
        color = "blue" if int(agent.vote) == 1 else "green"

    return {
        "id": agent.unique_id,
        "color": color,
        "marker": marker,
        "size": 15,
        "shapley": s_val  
    }

# =========================================================================
# CONFIGURAZIONE CANVAS ALTAIR
# =========================================================================
def make_space(chart):
    return (
        chart
        .mark_point(opacity=0.8, filled=True, size=225)
        .encode(
            shape=alt.Shape(
                "marker:N",
                scale=alt.Scale(
                    domain=["square", "circle", "diamond"],
                    range=["square", "circle", "diamond"]
                ),
                legend=None
            ),
            color=alt.Color("color:N", scale=None), 
            tooltip=["id:N", "shapley:Q"]
        )
        .properties(width=700, height=700)
    )

grid_component = make_space_component(
    agent_portrayal=voting_agent_portrayal, 
    backend="altair",
    post_process=make_space,
)

# =========================================================================
# INTERFACCIA UTENTE (SOLARA COMPONENT)
# =========================================================================
@solara.component
def CustomLayoutWrapper(model):
    
    grid_component(model)

    with solara.Card("Visualization Settings"):
        solara.Checkbox(
            label="Show Agent Markers by Vote (0=Circle, 1=Square)",
            value=use_vote_markers,
        )
        solara.Checkbox(
            label="Attiva Heatmap (Solo agenti in lista Shapley)",
            value=show_heatmap,
        )
    
    with solara.Card("Manual Agent Team Editor", style="width: 400px; margin: 20px auto;"):
        solara.InputText(
            label="Enter Agent ID", 
            value=typed_agent_id,
            continuous_update=False
        )
        
        def modify_agent_by_id():
            if not typed_agent_id.value.isdigit():
                return
            target_id = int(typed_agent_id.value)
            
            # Ricerca diretta corretta per il tuo modello Mesa
            target_agent = model.agents[target_id - 1]
                
            if target_agent:
                print(f"Successfully flipped agent ID: {target_id}")
                target_agent.change_vote()
                target_agent.is_ko = True  # Applica il flag di KO permanente
            
        solara.Button(
            label="Toggle Vote Team (Trigger KO)", 
            on_click=modify_agent_by_id, 
            color="primary",
            style="margin-top: 10px; width: 100%;"
        )

# =========================================================================
# INIZIALIZZAZIONE APPLICAZIONE MESA
# =========================================================================
initial_model = VotingGrid1()

model_params = {
    "size": {"type": "InputText", "value": 30, "label": "Grid Width and Height"},
    "activation_order": {
        "type": "Select",
        "value": "Random",
        "values": VotingGrid1.activation_regimes,
        "label": "Activation Regime",
    },
}

page = SolaraViz(
    model=initial_model,
    components=[CustomLayoutWrapper], 
    model_params=model_params,
    name="Voting from NetLogo",
)
page