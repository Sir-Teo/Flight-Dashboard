from dash import dcc, html
import dash_bootstrap_components as dbc

def create_app_layout(data):
    client_names = sorted(data['Client Name'].unique())
    return dbc.Container([
        html.H1("Flight Connections Dashboard", className="text-center my-4 chart-title"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='client-dropdown',
                    options=[{'label': client, 'value': client} for client in client_names],
                    value=client_names[0],
                    className="mb-3"
                )
            ], width={"size": 6, "offset": 3}),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='flight-connections-map', style={'height': '70vh'})
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='click-data', className="mt-3")
            ])
        ])
    ], fluid=True)