from dash import Input, Output
from map_utils import create_map_figure

def register_callbacks(app, data):
    @app.callback(
        Output('flight-connections-map', 'figure'),
        Output('click-data', 'children'),
        Input('client-dropdown', 'value'),
        Input('flight-connections-map', 'clickData')
    )
    def update_graph(selected_client, click_data):
        client_data = data[data['Client Name'] == selected_client]
        fig = create_map_figure(client_data, selected_client)
        
        click_info = "Click on a point to see more information."
        if click_data:
            point = click_data['points'][0]
            if 'text' in point:
                click_info = f"Clicked on: {point['text']}"
            elif 'hovertext' in point:
                click_info = point['hovertext']
        
        return fig, click_info
