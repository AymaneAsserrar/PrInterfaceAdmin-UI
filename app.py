import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd

# Configuration de l'API
RAM_INFO_URL = 'http://0.0.0.0:8000/metrics/v1/ram/info'
CPU_API_URL = 'http://0.0.0.0:8000/metrics/v1/cpu/usage'

def fetch_ram_info():
    try:
        response = requests.get(RAM_INFO_URL)
        return response.json()
    except Exception as e:
        print(f"Erreur de récupération des données RAM : {e}")
        return {}

def prepare_ram_gauge_data(ram_info):
    if not ram_info:
        return 0
    
    total = ram_info.get('total', 0)
    used = ram_info.get('used', 0)
    
    # Calculer le pourcentage d'utilisation
    usage_percent = (used / total * 100) if total > 0 else 0
    return usage_percent

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout du dashboard
app.layout = dbc.Container([
    html.H1("Monitoring RAM", className="text-center my-4"),
    
    # Première ligne avec les métriques RAM
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("RAM Totale", className="text-center"),
                    html.H2(id="ram-total", className="text-center"),
                    html.P(id="ram-total-gb", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("RAM Utilisée", className="text-center"),
                    html.H2(id="ram-used", className="text-center"),
                    html.P(id="ram-used-gb", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("RAM Disponible", className="text-center"),
                    html.H2(id="ram-available", className="text-center"),
                    html.P(id="ram-available-gb", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("RAM Libre", className="text-center"),
                    html.H2(id="ram-free", className="text-center"),
                    html.P(id="ram-free-gb", className="text-center text-muted")
                ])
            ])
        ], width=3),
    ], className="mb-4"),
    
    # Deuxième ligne avec le graphique gauge
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='ram-gauge')
        ], width=12)
    ]),
    
    # Composant d'intervalle pour les mises à jour
    dcc.Interval(
        id='interval-component',
        interval=3000,  # Mise à jour toutes les 3 secondes
        n_intervals=0
    )
], fluid=True)

def format_memory(mb_value):
    """Convertit les mégaoctets en format lisible (MB et GB)"""
    gb_value = mb_value / 1024
    return f"{mb_value:.0f} MB", f"({gb_value:.2f} GB)"

@app.callback(
    [
        Output("ram-total", "children"),
        Output("ram-total-gb", "children"),
        Output("ram-used", "children"),
        Output("ram-used-gb", "children"),
        Output("ram-available", "children"),
        Output("ram-available-gb", "children"),
        Output("ram-free", "children"),
        Output("ram-free-gb", "children"),
        Output("ram-gauge", "figure")
    ],
    Input("interval-component", "n_intervals")
)
def update_metrics(_):
    ram_info = fetch_ram_info()
    
    # Formatage des valeurs RAM
    total_mb, total_gb = format_memory(ram_info.get('total', 0))
    used_mb, used_gb = format_memory(ram_info.get('used', 0))
    available_mb, available_gb = format_memory(ram_info.get('available', 0))
    free_mb, free_gb = format_memory(ram_info.get('free', 0))
    
    # Création du graphique gauge
    usage_percent = prepare_ram_gauge_data(ram_info)
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=usage_percent,
        title={'text': "Utilisation RAM (%)"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    gauge_fig.update_layout(height=400)
    
    return total_mb, total_gb, used_mb, used_gb, available_mb, available_gb, free_mb, free_gb, gauge_fig

if __name__ == '__main__':
    app.run_server(debug=True)