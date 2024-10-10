import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

MAX_CONNECTIONS = 100
BUBBLE_COLOR_SCALE = [
    [0, "#FFF7FB"], [0.2, "#ECE7F2"], [0.4, "#D0D1E6"],
    [0.6, "#A6BDDB"], [0.8, "#74A9CF"], [1, "#2B8CBE"],
]

import plotly.colors

def create_map_figure(client_data, selected_client):
    # Sort the data by Depart_Days_Count_Sum and get the top 100 routes
    top_100_routes = client_data.sort_values('Depart_Days_Count_Sum', ascending=False).head(100)
    
    # Get Viridis color scale
    viridis_colors = px.colors.sequential.Viridis

    # Normalize Depart_Days_Count_Sum for color mapping
    norm_depart_days = np.interp(top_100_routes['Depart_Days_Count_Sum'], 
                                 [top_100_routes['Depart_Days_Count_Sum'].min(), top_100_routes['Depart_Days_Count_Sum'].max()], 
                                 [0, 1])

    fig = go.Figure()

    # Add lines for top 100 routes
    for index, row in top_100_routes.iterrows():
        # Normalize the current Depart_Days_Count_Sum value to pick a color
        normalized_value = np.interp(row['Depart_Days_Count_Sum'], 
                                     [top_100_routes['Depart_Days_Count_Sum'].min(), top_100_routes['Depart_Days_Count_Sum'].max()], 
                                     [0, 1])
        # Get the color for the current value from the Viridis color scale
        line_color = plotly.colors.sample_colorscale(viridis_colors, normalized_value)[0]
        
        line_width = np.interp(row['Depart_Days_Count_Sum'], [top_100_routes['Depart_Days_Count_Sum'].min(), top_100_routes['Depart_Days_Count_Sum'].max()], [1, 10])
        
        fig.add_trace(go.Scattergeo(
            lon=[row['origincity_long'], row['destcity_long']],
            lat=[row['origincity_lat'], row['destcity_lat']],
            mode='lines',
            line=dict(width=line_width, color=line_color),
            hoverinfo="text",
            hovertext=f"{row['origincity_code']} to {row['destcity_code']}<br>"
                      f"Depart Days: {row['Depart_Days_Count_Sum']:,}<br>"
                      f"Competitors: {row['all_competitors']}",
            customdata=[row['Depart_Days_Count_Sum'], row['all_competitors']],
        ))

    # Calculate total depart days for each city
    city_depart_days = client_data.groupby('origincity_code')['Depart_Days_Count_Sum'].sum().reset_index()

    # Add markers for origin and destination cities
    unique_cities = pd.concat([
        top_100_routes[['origincity_code', 'origincity_lat', 'origincity_long']].rename(columns={'origincity_code': 'city_code', 'origincity_lat': 'lat', 'origincity_long': 'lon'}),
        top_100_routes[['destcity_code', 'destcity_lat', 'destcity_long']].rename(columns={'destcity_code': 'city_code', 'destcity_lat': 'lat', 'destcity_long': 'lon'})
    ]).drop_duplicates()

    # Merge with city_depart_days to get the total depart days for each city
    unique_cities = unique_cities.merge(city_depart_days, left_on='city_code', right_on='origincity_code', how='left')
    unique_cities['Depart_Days_Count_Sum'] = unique_cities['Depart_Days_Count_Sum'].fillna(0)

    # Calculate marker sizes based on Depart_Days_Count_Sum
    marker_sizes = np.interp(unique_cities['Depart_Days_Count_Sum'], 
                             [unique_cities['Depart_Days_Count_Sum'].min(), unique_cities['Depart_Days_Count_Sum'].max()], 
                             [5, 20])

    fig.add_trace(go.Scattergeo(
        lon=unique_cities['lon'],
        lat=unique_cities['lat'],
        text=unique_cities['city_code'],
        mode='markers',
        marker=dict(
            size=marker_sizes,
            color=unique_cities['Depart_Days_Count_Sum'],
            colorscale='Viridis',
            colorbar=dict(
                title='Depart Days',
                x=1.2, 
                xanchor='left',
                y=0.5,  # Center the colorbar vertically
                len=1  # Adjust the length of the colorbar
            ),
            cmin=unique_cities['Depart_Days_Count_Sum'].min(),
            cmax=unique_cities['Depart_Days_Count_Sum'].max(),
            opacity=0.8
        ),
        hoverinfo="text",
        hovertext=[f"{row['city_code']}<br>Depart Days: {row['Depart_Days_Count_Sum']:,}<br>Competitors: {client_data[client_data['origincity_code'] == row['city_code']]['all_competitors'].iloc[0]}" for _, row in unique_cities.iterrows()],
    ))

    update_layout(fig, client_data, selected_client)
    return fig

def update_layout(fig, client_data, selected_client):
    fig.update_layout(
        title={
            'text': f"Top 100 Flight Connections for {selected_client}",
            'font': {'size': 24, 'color': '#2B8CBE'},
            'x': 0.5,
            'xanchor': 'center'
        },
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=client_data['origincity_lat'].mean(), lon=client_data['origincity_long'].mean()),
            zoom=2,
        ),
        height=800,
        margin=dict(l=0, r=0, t=50, b=0),
    )
