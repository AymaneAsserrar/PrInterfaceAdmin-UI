"""
Complete monitoring dashboard application with CPU and RAM metrics visualization.
Save this as 'app.py'
"""
import dash
from dash import dcc, html, ALL
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from dash.exceptions import PreventUpdate
import re
from collections import deque, defaultdict
from datetime import datetime
import psutil
import json
import random

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Constants
MAX_HISTORY_LENGTH = 50
DEFAULT_REFRESH_RATE = 3000  # 3 seconds

# Server data storage
class ServerMetricsHistory:
    def __init__(self):
        self.timestamps = deque(maxlen=MAX_HISTORY_LENGTH)
        self.cpu_averages = deque(maxlen=MAX_HISTORY_LENGTH)
        self.cpu_per_core = [deque(maxlen=MAX_HISTORY_LENGTH) for _ in range(32)]
        self.ram_usage = deque(maxlen=MAX_HISTORY_LENGTH)

class ServerManager:
    def __init__(self):
        self.servers = {}  # Dictionary to store server configurations
        self.metrics_history = defaultdict(ServerMetricsHistory)
        self.load_servers()

    def load_servers(self):
        try:
            with open('servers.json', 'r') as f:
                self.servers = json.load(f)
        except FileNotFoundError:
            self.servers = {}

    def save_servers(self):
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f)

    def add_server(self, ip, port, nickname, hostname):
        server_id = f"{ip}:{port}"
        self.servers[server_id] = {
            'ip': ip,
            'port': port,
            'nickname': nickname,
            'hostname': hostname,
            'last_seen': None,
            'cpu_info': None,
            'ram_info': None
        }
        self.save_servers()

    def remove_server(self, server_id):
        if server_id in self.servers:
            del self.servers[server_id]
            self.save_servers()

    def get_server_metrics(self, server_id):
        if server_id not in self.servers:
            return None
        server = self.servers[server_id]
        return self.fetch_metrics(server['ip'], server['port'])

    def fetch_metrics(self, ip, port):
        try:
            # Basic health check
            health_url = f"http://{ip}:{port}/health"
            health_response = requests.get(health_url, timeout=5)
            is_healthy = health_response.status_code == 200

            if not is_healthy:
                return {'health': False}

            # Fetch metrics in parallel using a session
            with requests.Session() as session:
                try:
                    # CPU metrics
                    cpu_url = f"http://{ip}:{port}/metrics/v1/cpu/usage"
                    cpu_response = session.get(cpu_url, timeout=5)
                    cpu_data = cpu_response.json()
                except:
                    cpu_data = {'average': 0, 'per_core': []}

                try:
                    # RAM info metrics
                    ram_info_url = f"http://{ip}:{port}/metrics/v1/ram/info"
                    ram_info_response = session.get(ram_info_url, timeout=5)
                    ram_info = ram_info_response.json()
                except:
                    ram_info = {'total': 0, 'available': 0, 'used': 0, 'free': 0}

                try:
                    # RAM usage metrics
                    ram_usage_url = f"http://{ip}:{port}/metrics/v1/ram/usage"
                    ram_usage_response = session.get(ram_usage_url, timeout=5)
                    ram_usage_data = ram_usage_response.json()
                    # Get the first usage value or default to 0
                    ram_usage = float(ram_usage_data[0]['usage']) if ram_usage_data else 0
                except:
                    ram_usage = 0

                # Combine RAM data
                ram_data = {
                    **ram_info,  # Include all RAM info fields
                    'usage_percent': ram_usage  # Add usage percentage
                }

                return {
                    'health': True,
                    'cpu': cpu_data,
                    'ram': ram_data
                }

        except Exception as e:
            print(f"Error fetching metrics for {ip}:{port}: {str(e)}")
            return {'health': False}

server_manager = ServerManager()

def format_memory(mb_value):
    gb_value = mb_value / 1024
    return f"{mb_value:.0f} MB", f"({gb_value:.2f} GB)"

def is_valid_ip(ip):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(octet) <= 255 for octet in ip.split('.'))

# Layout components
def create_server_card(server_id, server_info, metrics):
    is_healthy = metrics.get('health', False) if metrics else False
    cpu_usage = metrics.get('cpu', {}).get('average', 0) if metrics else 0
    ram_usage = metrics.get('ram', {}).get('usage_percent', 0) if metrics else 0

    return dbc.Card([
        dbc.CardHeader([
            html.H4(server_info['nickname'], className="d-inline me-2"),
            dbc.Button(
                "×",
                id={'type': 'remove-btn', 'index': server_id},
                className="btn-close float-end",
                n_clicks=0
            )
        ]),
        dbc.CardBody([
            html.P(f"Hostname: {server_info['hostname']}"),
            html.P(f"IP: {server_info['ip']}:{server_info['port']}"),
            html.P([
                "Status: ",
                html.Span(
                    "Reachable" if is_healthy else "Unreachable",
                    className=f"text-{'success' if is_healthy else 'danger'}"
                )
            ]),
            html.P(f"CPU Usage: {cpu_usage:.1f}%"),
            html.P(f"RAM Usage: {ram_usage:.1f}%"),
            dbc.Button(
                "View Details",
                href=f"/server/{server_id}",
                color="primary",
                size="sm",
                className="mt-2"
            )
        ])
    ], className="mb-4")

# Main dashboard layout
main_layout = dbc.Container([
    html.H1("Server Monitoring Dashboard", className="text-center my-4"),
    dbc.Row([
        dbc.Col([
            dbc.Button("Add Server", id="add-server-button", color="primary", className="mb-4"),
            html.Div(id="servers-grid", children=[]),  # Initialize with empty children
            dbc.Modal([
                dbc.ModalHeader("Add New Server"),
                dbc.ModalBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("IP Address"),
                                dbc.Input(id="new-server-ip", type="text", placeholder="Enter IP address", className="mb-3")
                            ]),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Port"),
                                dbc.Input(id="new-server-port", type="number", placeholder="Enter port number", className="mb-3")
                            ]),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Nickname"),
                                dbc.Input(id="new-server-nickname", type="text", placeholder="Enter server nickname", className="mb-3")
                            ]),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Hostname"),
                                dbc.Input(id="new-server-hostname", type="text", placeholder="Enter hostname", className="mb-3")
                            ]),
                        ])
                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="add-server-cancel", className="me-2"),
                    dbc.Button("Add Server", id="add-server-submit", color="primary")
                ])
            ], id="add-server-modal", is_open=False),
            dcc.Interval(
                id='refresh-interval',
                interval=DEFAULT_REFRESH_RATE,
                n_intervals=0
            ),
            dcc.Store(id='refresh-rate-store', data=DEFAULT_REFRESH_RATE),
            dcc.Store(id='callback-trigger', data=0)
        ])
    ])
], fluid=True)

# Server detail layout
def create_server_detail_layout(server_id):
    server = server_manager.servers.get(server_id)
    if not server:
        return html.H1("Server not found")

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(f"Server Details - {server['nickname']}", className="text-center my-4"),
                dbc.Button("← Back to Dashboard", href="/", color="secondary", className="mb-4")
            ])
        ]),
        
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

        # Refresh rate control
        dbc.Card([
            dbc.CardBody([
                html.H5("Refresh Rate"),
                dcc.Slider(
                    id="refresh-rate-slider",
                    min=1,
                    max=60,
                    step=1,
                    value=DEFAULT_REFRESH_RATE / 1000,
                    marks={i: f"{i}s" for i in [1, 15, 30, 45, 60]},
                    className="mb-4"
                )
            ])
        ], className="mt-4"),
        
        dcc.Interval(id='detail-refresh', interval=DEFAULT_REFRESH_RATE),
        dcc.Store(id='server-id-store', data=server_id)
    ], fluid=True)

# Main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/' or pathname is None:
        return main_layout
    elif pathname.startswith('/server/'):
        server_id = pathname.split('/')[-1]
        return create_server_detail_layout(server_id)
    return '404 - Page not found'

@app.callback(
    Output("add-server-modal", "is_open"),
    [
        Input("add-server-button", "n_clicks"),
        Input("add-server-cancel", "n_clicks"),
        Input("add-server-submit", "n_clicks"),
    ],
    [State("add-server-modal", "is_open")],
)
def toggle_modal(n_open, n_cancel, n_submit, is_open):
    if n_open or n_cancel or n_submit:
        return not is_open
    return is_open

@app.callback(
    Output('callback-trigger', 'data'),
    [Input({'type': 'remove-btn', 'index': ALL}, 'n_clicks')]
)
def handle_remove_server(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        button_data = json.loads(button_id)
        if button_data['type'] == 'remove-btn':
            server_id = button_data['index']
            server_manager.remove_server(server_id)
            return datetime.now().timestamp()
    except Exception as e:
        print(f"Error removing server: {e}")
    
    raise PreventUpdate
# Extract server ID from button ID
    server_id = button_id.replace('remove-server-', '')
    try:
        server_manager.remove_server(server_id)
        return datetime.now().timestamp()
    except Exception as e:
        print(f"Error removing server: {e}")
        raise PreventUpdate

@app.callback(
    [Output('servers-grid', 'children'),
     Output('new-server-ip', 'value'),
     Output('new-server-port', 'value'),
     Output('new-server-nickname', 'value'),
     Output('new-server-hostname', 'value')],
    [Input('refresh-interval', 'n_intervals'),
     Input('add-server-submit', 'n_clicks'),
     Input('callback-trigger', 'data')],
    [State('new-server-ip', 'value'),
     State('new-server-port', 'value'),
     State('new-server-nickname', 'value'),
     State('new-server-hostname', 'value')]
)
def update_servers_grid(n_intervals, add_clicks, trigger, new_ip, new_port, new_nickname, new_hostname):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'add-server-submit' and all([new_ip, new_port, new_nickname, new_hostname]):
        try:
            server_manager.add_server(new_ip, int(new_port), new_nickname, new_hostname)
            return update_grid(), "", "", "", ""
        except Exception as e:
            print(f"Error adding server: {e}")
            return update_grid(), new_ip, new_port, new_nickname, new_hostname
    
    return update_grid(), dash.no_update, dash.no_update, dash.no_update, dash.no_update

def update_grid():
    cards = []
    for server_id, server_info in server_manager.servers.items():
        metrics = server_manager.get_server_metrics(server_id)
        cards.append(create_server_card(server_id, server_info, metrics))
    
    return dbc.Row([dbc.Col(card, width=12, md=6, lg=4) for card in cards])

# Add server detail metrics callback
@app.callback(
    [
        Output("error-message", "children"),
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
        Output("ram-free-gb", "children")
    ],
    [Input("detail-refresh", "n_intervals")],
    [State("server-id-store", "data")]
)
def update_server_metrics(n_intervals, server_id):
    if not server_id or server_id not in server_manager.servers:
        return ["Server not found"] + [dash.no_update] * 15

    try:
        # Get metrics from server manager
        metrics = server_manager.get_server_metrics(server_id)
        
        if not metrics or not metrics.get('health', False):
            return ["Server is unreachable"] + [dash.no_update] * 15

        # Update metrics history
        history = server_manager.metrics_history[server_id]
        current_time = datetime.now()
        
        history.timestamps.append(current_time)
        history.cpu_averages.append(metrics['cpu']['average'])
        history.ram_usage.append(metrics['ram'].get('usage_percent', 0))
        
        # Update per-core history
        for i, core in enumerate(metrics['cpu'].get('per_core', [])):
            while len(history.cpu_per_core) <= i:
                history.cpu_per_core.append(deque(maxlen=MAX_HISTORY_LENGTH))
            history.cpu_per_core[i].append(core)

        # Create CPU history graph
        cpu_history_fig = go.Figure()
        cpu_history_fig.add_trace(go.Scatter(
            x=list(history.timestamps),
            y=list(history.cpu_averages),
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
        for i, core_usage in enumerate(metrics['cpu'].get('per_core', [])):
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
            yaxis=dict(range=[0, 100])
        )

        # Create RAM history graph
        ram_history_fig = go.Figure()
        ram_history_fig.add_trace(go.Scatter(
            x=list(history.timestamps),
            y=list(history.ram_usage),
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
        ram_usage_percent = metrics['ram'].get('usage_percent', 0)
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
        total_mb, total_gb = format_memory(metrics['ram'].get('total', 0))
        used_mb, used_gb = format_memory(metrics['ram'].get('used', 0))
        available_mb, available_gb = format_memory(metrics['ram'].get('available', 0))
        free_mb, free_gb = format_memory(metrics['ram'].get('free', 0))

        return [
            "",  # Clear error message
            "Reachable",
            "text-success",
            f"{metrics['cpu']['average']:.1f}%",
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
        print(f"Error updating metrics: {str(e)}")
        return [f"Error updating metrics: {str(e)}"] + [dash.no_update] * 15

# Refresh rate update callback
@app.callback(
    Output('detail-refresh', 'interval'),
    [Input('refresh-rate-slider', 'value')]
)
def update_refresh_rate(value):
    interval = value * 1000  # Convert seconds to milliseconds
    return interval

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)