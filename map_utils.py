import plotly.express as px
import plotly.graph_objects as go
import numpy as np

MAX_CONNECTIONS = 150
BUBBLE_COLOR_SCALE = [
    [0, "#FFF7FB"], [0.2, "#ECE7F2"], [0.4, "#D0D1E6"],
    [0.6, "#A6BDDB"], [0.8, "#74A9CF"], [1, "#2B8CBE"],
]

import pandas as pd

def create_map_figure(client_data, selected_client):
    if len(client_data) <= 1:
        return go.Figure().add_annotation(text=f"Insufficient data for {selected_client}", showarrow=False)
    
    # Group by city and aggregate depart days, concatenate competitors
    client_data_grouped = client_data.groupby('origincity_code', as_index=False).agg({
        'sum': 'sum',  # Aggregating departure days by sum
        'origincity_lat': 'first',
        'origincity_long': 'first',
        'country_code_origin': 'first',
        'competitors': lambda x: ', '.join(x.unique())  # Combine all unique competitors into a single string
    })
    
    # Create the base map with the modified hover information
    fig = create_base_map(client_data_grouped)
    
    # Add connections to the map and retain the legend functionality for competitors
    add_connections_to_map(fig, client_data_grouped)
    update_layout(fig, client_data_grouped, selected_client)
    add_top_cities_annotations(fig, client_data_grouped)
    add_explanation_annotation(fig)
    
    # Keep the original legend for competitors
    add_competitor_legend(fig, client_data)  # Passing the original client_data to retain distinct competitors

    return fig

def create_base_map(client_data):
    return px.scatter_mapbox(
        client_data, 
        lat="origincity_lat", 
        lon="origincity_long", 
        hover_name="origincity_code",
        hover_data={
            "country_code_origin": True, 
            "sum": True, 
            "origincity_lat": False, 
            "origincity_long": False, 
            "competitors": True  # Show all competitors in the hover text
        },
        size='sum',
        color='sum',
        size_max=40,
        zoom=2,
        mapbox_style="carto-positron",
        color_continuous_scale=BUBBLE_COLOR_SCALE
    )


def add_connections_to_map(fig, client_data):
    client_data_sorted = client_data.sort_values('sum', ascending=False)
    max_sum = client_data['sum'].max()
    competitor_color_scale = px.colors.qualitative.Bold

    for i in range(min(len(client_data_sorted) - 1, MAX_CONNECTIONS)):
        start, end = client_data_sorted.iloc[i], client_data_sorted.iloc[i+1]
        line_width = np.interp(start['sum'], [client_data_sorted['sum'].min(), max_sum], [1, 10])
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

def update_layout(fig, client_data, selected_client):
    fig.update_layout(
        title={
            'text': f"Top {MAX_CONNECTIONS} Flight Connections for {selected_client}",
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

def add_top_cities_annotations(fig, client_data):
    top_5_cities = client_data.sort_values('sum', ascending=False).head()
    for _, row in top_5_cities.iterrows():
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

def add_explanation_annotation(fig):
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.15,
        text=f"Bubble size and color intensity represent the number of departure days.<br>Lines show top {MAX_CONNECTIONS} connections, with thickness indicating importance and color representing competitors.",
        showarrow=False,
        font=dict(size=12),
        align="left",
        bgcolor="white",
        opacity=0.8,
        bordercolor="black",
        borderwidth=1
    )

def add_competitor_legend(fig, client_data):
    competitor_color_scale = px.colors.qualitative.Bold
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