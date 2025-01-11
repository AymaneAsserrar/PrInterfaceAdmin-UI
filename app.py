"""
Complete monitoring dashboard application with CPU and RAM metrics visualization.
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from dash.exceptions import PreventUpdate
import re
from collections import deque
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Create deques for historical data
MAX_HISTORY_LENGTH = 50

class MetricsHistory:
    def __init__(self):
        self.timestamps = deque(maxlen=MAX_HISTORY_LENGTH)
        self.cpu_averages = deque(maxlen=MAX_HISTORY_LENGTH)
        self.cpu_per_core = [deque(maxlen=MAX_HISTORY_LENGTH) for _ in range(32)]
        self.ram_usage = deque(maxlen=MAX_HISTORY_LENGTH)

metrics_history = MetricsHistory()

# Helper functions
def check_health(ip):
    try:
        health_url = f"http://{ip}:8000/health"
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def fetch_cpu_usage(ip):
    try:
        cpu_url = f"http://{ip}:8000/metrics/v1/cpu/usage"
        response = requests.get(cpu_url, timeout=5)
        data = response.json()
        return {
            'average': data.get('average', 0),
            'per_core': [core['usage'] for core in data.get('cpu_usage', [])]
        }
    except Exception as e:
        print(f"CPU data fetch error: {e}")
        return {'average': 0, 'per_core': []}

def fetch_ram_info(ip):
    try:
        ram_url = f"http://{ip}:8000/metrics/v1/ram/info"
        response = requests.get(ram_url, timeout=5)
        return response.json()
    except Exception as e:
        print(f"RAM data fetch error: {e}")
        return {}

def format_memory(mb_value):
    gb_value = mb_value / 1024
    return f"{mb_value:.0f} MB", f"({gb_value:.2f} GB)"

def prepare_ram_gauge_data(ram_info):
    if not ram_info:
        return 0
    total = ram_info.get('total', 0)
    used = ram_info.get('used', 0)
    return (used / total * 100) if total > 0 else 0

def is_valid_ip(ip):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(octet) <= 255 for octet in ip.split('.'))

# Define layouts
home_layout = dbc.Container([
    html.Div([
        html.H1("Server Monitoring Dashboard", className="text-center my-4"),
        dbc.Card([
            dbc.CardBody([
                html.H4("Enter Server Details", className="text-center mb-4"),
                dbc.Input(
                    id="ip-input",
                    placeholder="Enter server IP address",
                    type="text",
                    className="mb-3"
                ),
                html.Div(id="ip-error-message", className="text-danger mb-3"),
                dbc.Button(
                    "Connect",
                    id="connect-button",
                    color="primary",
                    className="w-100"
                )
            ])
        ], className="shadow-sm")
    ], style={'max-width': '500px', 'margin': '0 auto', 'padding-top': '100px'})
], fluid=True)

def create_metrics_layout(ip):
    return dbc.Container([
        html.H1(f"Server Metrics - {ip}", className="text-center my-4"),
        dbc.Button("← Back", id="back-button", color="secondary", className="mb-4"),
        
        # Error message div
        html.Div(id="error-message", className="text-danger mb-4"),
        
        # Health Status Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Server Health", className="text-center"),
                        html.H2(id="health-status", className="text-center text-success")
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # CPU Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("CPU Metrics", className="text-center")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Average CPU Usage", className="text-center mb-3"),
                                html.H2(id="cpu-usage", className="text-center")
                            ], width=12),
                        ]),
                        dcc.Graph(id='cpu-history-graph'),
                        dcc.Graph(id='cpu-cores-graph')
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # RAM Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("RAM Metrics", className="text-center")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='ram-gauge')
                            ], width=6),
                            dbc.Col([
                                dcc.Graph(id='ram-history-graph')
                            ], width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Total RAM"),
                                html.H3(id="ram-total"),
                                html.P(id="ram-total-gb", className="text-muted")
                            ], width=3),
                            dbc.Col([
                                html.H5("Used RAM"),
                                html.H3(id="ram-used"),
                                html.P(id="ram-used-gb", className="text-muted")
                            ], width=3),
                            dbc.Col([
                                html.H5("Available RAM"),
                                html.H3(id="ram-available"),
                                html.P(id="ram-available-gb", className="text-muted")
                            ], width=3),
                            dbc.Col([
                                html.H5("Free RAM"),
                                html.H3(id="ram-free"),
                                html.P(id="ram-free-gb", className="text-muted")
                            ], width=3),
                        ])
                    ])
                ])
            ], width=12)
        ]),

        # Interval component and store
        dcc.Interval(id='interval-component', interval=3000, n_intervals=0),
        dcc.Store(id='ip-store', data=ip)
    ], fluid=True)

# Define the main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callbacks
@app.callback(
    [Output('url', 'pathname'),
     Output('ip-error-message', 'children')],
    [Input('connect-button', 'n_clicks')],
    [State('ip-input', 'value')]
)
def validate_and_navigate(n_clicks, ip):
    if n_clicks is None:
        raise PreventUpdate
    
    if not ip:
        return dash.no_update, "Please enter an IP address"
    
    if not is_valid_ip(ip):
        return dash.no_update, "Please enter a valid IP address"
    
    return f'/metrics/{ip}', ""

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/' or pathname is None:
        return home_layout
    elif pathname.startswith('/metrics/'):
        ip = pathname.split('/')[-1]
        return create_metrics_layout(ip)
    else:
        return '404 - Page not found'

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('back-button', 'n_clicks')],
    prevent_initial_call=True
)
def go_back(n_clicks):
    if n_clicks:
        return '/'
    raise PreventUpdate

@app.callback(
    [Output("error-message", "children"),
     Output("health-status", "children"),
     Output("health-status", "className"),
     Output("cpu-usage", "children"),
     Output("cpu-history-graph", "figure"),
     Output("cpu-cores-graph", "figure"),
     Output("ram-history-graph", "figure"),
     Output("ram-gauge", "figure"),
     Output("ram-total", "children"),
     Output("ram-total-gb", "children"),
     Output("ram-used", "children"),
     Output("ram-used-gb", "children"),
     Output("ram-available", "children"),
     Output("ram-available-gb", "children"),
     Output("ram-free", "children"),
     Output("ram-free-gb", "children")],
    [Input("interval-component", "n_intervals"),
     Input("ip-store", "data")]
)
def update_metrics(n_intervals, ip):
    if not ip:
        return ["No IP address provided"] + [dash.no_update] * 15
    
    try:
        # Check health
        is_healthy = check_health(ip)
        if not is_healthy:
            return ["Server is unreachable"] + [dash.no_update] * 15

        # Fetch metrics
        cpu_data = fetch_cpu_usage(ip)
        ram_info = fetch_ram_info(ip)
        
        if not ram_info:
            return ["Failed to fetch RAM information"] + [dash.no_update] * 15

        # Update history
        current_time = datetime.now()
        metrics_history.timestamps.append(current_time)
        metrics_history.cpu_averages.append(cpu_data['average'])
        ram_usage_percent = prepare_ram_gauge_data(ram_info)
        metrics_history.ram_usage.append(ram_usage_percent)
        
        for i, usage in enumerate(cpu_data['per_core']):
            while len(metrics_history.cpu_per_core) <= i:
                metrics_history.cpu_per_core.append(deque(maxlen=MAX_HISTORY_LENGTH))
            metrics_history.cpu_per_core[i].append(usage)

        # Create CPU history graph
        cpu_history_fig = go.Figure()
        cpu_history_fig.add_trace(go.Scatter(
            x=list(metrics_history.timestamps),
            y=list(metrics_history.cpu_averages),
            name="CPU Average",
            line=dict(color='blue')
        ))
        cpu_history_fig.update_layout(
            title="CPU Usage History",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )

        # Create CPU cores graph
        cpu_cores_fig = go.Figure()
        for i, core_usage in enumerate(cpu_data['per_core']):
            cpu_cores_fig.add_trace(go.Bar(
                x=[f"Core {i}"],
                y=[core_usage],
                name=f"Core {i}"
            ))
        cpu_cores_fig.update_layout(
            title="CPU Usage Per Core",
            yaxis_title="Usage (%)",
            height=300,
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=False,
            yaxis=dict(range=[0, 100])  # Fixed y-axis range for better visualization
        )

        # Create RAM history graph
        ram_history_fig = go.Figure()
        ram_history_fig.add_trace(go.Scatter(
            x=list(metrics_history.timestamps),
            y=list(metrics_history.ram_usage),
            name="RAM Usage",
            line=dict(color='green')
        ))
        ram_history_fig.update_layout(
            title="RAM Usage History",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )

        # Create RAM gauge
        ram_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ram_usage_percent,
            title={'text': "RAM Usage (%)"},
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
        ram_gauge.update_layout(height=300)

        # Format RAM values
        total_mb, total_gb = format_memory(ram_info.get('total', 0))
        used_mb, used_gb = format_memory(ram_info.get('used', 0))
        available_mb, available_gb = format_memory(ram_info.get('available', 0))
        free_mb, free_gb = format_memory(ram_info.get('free', 0))

        return [
            "",  # Clear error message
            "Reachable" if is_healthy else "Unreachable",
            "text-success" if is_healthy else "text-danger",
            f"{cpu_data['average']:.1f}%",
            cpu_history_fig,
            cpu_cores_fig,
            ram_history_fig,
            ram_gauge,
            total_mb,
            total_gb,
            used_mb,
            used_gb,
            available_mb,
            available_gb,
            free_mb,
            free_gb
        ]

    except Exception as e:
        return [f"Error updating metrics: {str(e)}"] + [dash.no_update] * 15

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)