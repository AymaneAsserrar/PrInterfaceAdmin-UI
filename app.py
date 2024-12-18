import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import pandas as pd

# Configuration des API
RAM_API_URL = 'http://0.0.0.0:8000/metrics/v1/ram/usage'
CPU_API_URL = 'http://0.0.0.0:8000/metrics/v1/cpu/usage'

def fetch_ram_data():
    try:
        response = requests.get(RAM_API_URL)
        return response.json()
    except Exception as e:
        print(f"Erreur de récupération des données RAM : {e}")
        return []

def fetch_cpu_data():
    try:
        response = requests.get(CPU_API_URL)
        return response.json()
    except Exception as e:
        print(f"Erreur de récupération des données CPU : {e}")
        return []

def prepare_dashboard_data():
    ram_data = fetch_ram_data()
    cpu_data = fetch_cpu_data()
    
    # Vérification et transformation en DataFrame
    ram_df = pd.DataFrame(ram_data) if ram_data else pd.DataFrame(columns=['id', 'usage'])
    cpu_df = pd.DataFrame(cpu_data) if cpu_data else pd.DataFrame(columns=['id', 'usage'])
    
    # Renommer la colonne 'id' en 'server' si nécessaire
    ram_df.rename(columns={'id': 'server'}, inplace=True)
    cpu_df.rename(columns={'id': 'server'}, inplace=True)
    
    return ram_df, cpu_df

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout du dashboard
app.layout = dbc.Container([
    html.H1("Monitoring Serveur", className="text-center my-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='ram-usage-chart')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='cpu-usage-chart')
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Interval(
                id='interval-component',
                interval=60*1000,  # Mise à jour toutes les minutes
                n_intervals=0
            )
        ])
    ])
], fluid=True)

# Callback pour mettre à jour les graphiques
@app.callback(
    [Output('ram-usage-chart', 'figure'),
     Output('cpu-usage-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(_):
    ram_df, cpu_df = prepare_dashboard_data()
    
    # Graphique d'utilisation de la RAM
    ram_fig = px.bar(
        ram_df, 
        x='server', 
        y='usage', 
        title='Utilisation de la RAM par serveur',
        labels={'usage': 'Utilisation (%)', 'server': 'Serveur'}
    )
    
    # Graphique d'utilisation du CPU
    cpu_fig = px.bar(
        cpu_df, 
        x='server', 
        y='usage', 
        title='Utilisation du CPU par serveur',
        labels={'usage': 'Utilisation (%)', 'server': 'Serveur'}
    )
    
    return ram_fig, cpu_fig

if __name__ == '__main__':
    app.run_server(debug=True)
