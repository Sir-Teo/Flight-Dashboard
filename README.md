# Flight Dashboard

## Overview

The Flight Connections Dashboard is an interactive visualization tool that displays flight connection data for various clients. It provides a comprehensive view of departure frequencies, routes, and competitor information on a global map.

## Features

- Interactive map visualization of flight connections
- Client-specific data filtering
- Bubble chart representation of departure frequencies
- Color-coded competitor information
- Top connections highlighted with weighted lines
- Zoom and pan functionality for detailed exploration
- Click-to-filter for additional information on specific points
- Responsive design for various screen sizes
- Visually appealing color scheme and typography

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flight-connections-dashboard.git
   cd flight-connections-dashboard
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure you have the required data file (`parsed_data.csv`) in the project directory.

2. Run the Dash application:
   ```
   python app.py
   ```

3. Open a web browser and navigate to `http://127.0.0.1:8050/` to view the dashboard.

4. Use the dropdown menu to select different clients and explore their flight connection data.

5. Interact with the map:
   - Zoom in/out using the mouse wheel or touchpad gestures
   - Pan by clicking and dragging
   - Click on points to see additional information

6. Use the legend to filter connections by competitor

## Data Format

The dashboard expects a CSV file named `parsed_data.csv` with the following columns:

- Client Name
- country_code_origin
- origincity_code
- origincity_lat
- origincity_long
- competitors
- Depart Days Count

Ensure your data file follows this format for the dashboard to function correctly.

## Customization

You can customize the dashboard by modifying the following:

- Color schemes: Update the `bubble_color_scale` and `competitor_color_scale` variables in the code.
- Number of connections: Adjust the `top_connections` variable to show more or fewer connections.
- Styling: Modify the custom CSS in the `app.index_string` to change the overall look and feel.
