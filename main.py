from dash import Dash
import dash_bootstrap_components as dbc
from data_processing import load_and_process_data
from layout import create_app_layout
from callbacks import register_callbacks

FILE_PATH = 'client_depart_days_count_aggregated.csv'

def main():
    data = load_and_process_data(FILE_PATH)
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.index_string = get_custom_index_string()
    app.layout = create_app_layout(data)
    register_callbacks(app, data)
    app.run_server(debug=True)

def get_custom_index_string():
    return '''
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

if __name__ == '__main__':
    main()