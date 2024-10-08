import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# Load data
file_path = 'parsed_data.csv'
data = pd.read_csv(file_path)

# Group by 'Client Name', 'country_code_origin', 'origincity_code', and calculate 'sum' of 'Depart Days Count'
grouped_data = data.groupby(['Client Name', 'country_code_origin', 'origincity_code', 'origincity_lat', 'origincity_long', 'competitors'])['Depart Days Count'].agg(['sum']).reset_index()

# Get the unique client names
client_names = sorted(grouped_data['Client Name'].unique())

# Create a color scale for the bubble size and intensity
bubble_color_scale = [
    [0, "#FFF7FB"],    # Very light pink
    [0.2, "#ECE7F2"],  # Light lavender
    [0.4, "#D0D1E6"],  # Lavender
    [0.6, "#A6BDDB"],  # Light blue
    [0.8, "#74A9CF"],  # Medium blue
    [1, "#2B8CBE"],    # Dark blue
]

# Create a color scale for competitors
competitor_color_scale = px.colors.qualitative.Bold

# Initialize the Dash app with Bootstrap for responsive design
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Custom CSS for animations and improved typography
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f8f9fa;
            }
            .dash-graph {
                transition: all 0.3s ease-in-out;
            }
            .dash-graph:hover {
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .chart-title {
                font-weight: 700;
                color: #2B8CBE;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App layout with responsive design
app.layout = dbc.Container([
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

@app.callback(
    Output('flight-connections-map', 'figure'),
    Output('click-data', 'children'),
    Input('client-dropdown', 'value'),
    Input('flight-connections-map', 'clickData')
)
def update_graph(selected_client, click_data):
    client_data = grouped_data[grouped_data['Client Name'] == selected_client]
    
    if len(client_data) <= 1:
        return go.Figure().add_annotation(text=f"Insufficient data for {selected_client}", showarrow=False), "No data available"

    max_sum = client_data['sum'].max()
    
    fig = px.scatter_mapbox(client_data, 
                            lat="origincity_lat", 
                            lon="origincity_long", 
                            hover_name="origincity_code",
                            hover_data={"country_code_origin": True, "sum": True, "origincity_lat": False, "origincity_long": False, "competitors": True},
                            size='sum',
                            color='sum',
                            size_max=40,
                            zoom=2,
                            mapbox_style="carto-positron",
                            color_continuous_scale=bubble_color_scale)

    # Sort data by 'sum' in descending order to prioritize important connections
    client_data_sorted = client_data.sort_values('sum', ascending=False)
    
    # Select top 150 connections for visibility
    top_connections = 150
    for i in range(min(len(client_data_sorted) - 1, top_connections)):
        start = client_data_sorted.iloc[i]
        end = client_data_sorted.iloc[i+1]
        
        line_width = np.interp(start['sum'], [client_data_sorted['sum'].min(), max_sum], [1, 10])
        
        # Use the 'competitors' column to determine line color
        competitor_index = hash(start['competitors']) % len(competitor_color_scale)
        line_color = competitor_color_scale[competitor_index]

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[start['origincity_long'], end['origincity_long']],
            lat=[start['origincity_lat'], end['origincity_lat']],
            line=dict(width=line_width, color=line_color),
            hoverinfo='text',
            hovertext=f"From {start['origincity_code']} to {end['origincity_code']}<br>Depart Days: {start['sum']:,}<br>Competitors: {start['competitors']}",
            showlegend=False,
            opacity=0.7
        ))

    # Update the layout for better visibility and information
    fig.update_layout(
        title={
            'text': f"Top {top_connections} Flight Connections for {selected_client}",
            'font': {'size': 24, 'color': '#2B8CBE'},
            'x': 0.5,
            'xanchor': 'center'
        },
        mapbox=dict(
            center=dict(lat=client_data['origincity_lat'].mean(), lon=client_data['origincity_long'].mean()),
            zoom=2,
        ),
        coloraxis_colorbar=dict(
            title="Depart Days Count",
            titleside="top",
            tickformat=",",
            len=0.75,
            thickness=20,
            x=1.02,
            tickfont=dict(size=12),
            titlefont=dict(size=14)
        ),
        height=800,
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(
            title="Competitors",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="Black",
            borderwidth=1
        )
    )

    # Add annotations for top 5 cities
    top_5_cities = client_data_sorted.head()
    for idx, row in top_5_cities.iterrows():
        fig.add_annotation(
            x=row['origincity_long'],
            y=row['origincity_lat'],
            text=f"{row['origincity_code']}: {row['sum']:,}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#636363",
            font=dict(size=12, color="black"),
            bgcolor="white",
            opacity=0.8
        )

    # Add a text annotation explaining the visualization
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.15,
        text=f"Bubble size and color intensity represent the number of departure days.<br>Lines show top {top_connections} connections, with thickness indicating importance and color representing competitors.",
        showarrow=False,
        font=dict(size=12),
        align="left",
        bgcolor="white",
        opacity=0.8,
        bordercolor="black",
        borderwidth=1
    )

    # Add a legend for competitors
    unique_competitors = client_data['competitors'].unique()
    for i, competitor in enumerate(unique_competitors):
        color_index = hash(competitor) % len(competitor_color_scale)
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='lines',
            name=competitor,
            line=dict(color=competitor_color_scale[color_index], width=2),
            legendgroup=f"competitor_{i}",
            showlegend=True
        ))

    # Enable zoom and pan controls
    fig.update_layout(
        mapbox=dict(
            zoom=2,
            center=dict(lat=client_data['origincity_lat'].mean(), lon=client_data['origincity_long'].mean()),
        )
    )

    # Click data information
    click_info = "Click on a point to see more information."
    if click_data:
        point = click_data['points'][0]
        click_info = f"Clicked on: {point['hovertext']} - Depart Days: {point['customdata'][1]:,}"

    return fig, click_info

if __name__ == '__main__':
    app.run_server(debug=True)