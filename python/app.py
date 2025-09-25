import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json
import os

# added to handle relative path for JSON file
# replace with your desired file path
filename = os.path.join(os.path.dirname(__file__), "..", "assets", "air_quality_data.json")

# Load data from specified JSON file
with open(filename, "r") as file:
    data = json.load(file)

# Extract the 'Data' section into a DataFrame
data_section = data.get("Data", [])
df = pd.DataFrame(data_section)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Air Quality Dashboard"

# Layout of the app
app.layout = html.Div([
    html.H1("Air Quality Data Visualization", style={"textAlign": "center"}),

    # Dropdown to select a pollutant
    html.Label("Select Pollutant:"),
    dcc.Dropdown(
        id="pollutant-dropdown",
        options=[
            {"label": pollutant, "value": pollutant} for pollutant in df["parameter"].unique()
        ],
        value=df["parameter"].unique()[0],
        clearable=False
    ),

    # Graph to display pollutant levels over time
    dcc.Graph(id="time-series-graph"),

    # Map to display monitoring sites
    dcc.Graph(id="map-graph")
])

# Callback to update the time-series graph based on selected pollutant
@app.callback(
    Output("time-series-graph", "figure"),
    [Input("pollutant-dropdown", "value")]
)
def update_time_series(selected_pollutant):
    filtered_df = df[df["parameter"] == selected_pollutant]
    fig = px.scatter(
        filtered_df,
        x="first_max_datetime",
        y="arithmetic_mean",
        title=f"{selected_pollutant} Levels Over Time",
        labels={"first_max_datetime": "Date", "arithmetic_mean": "Pollutant Level"},
        hover_data=["local_site_name", "city"]
    )
    return fig

# Callback to update the map based on selected pollutant
@app.callback(
    Output("map-graph", "figure"),
    [Input("pollutant-dropdown", "value")]
)
def update_map(selected_pollutant):
    filtered_df = df[df["parameter"] == selected_pollutant]
    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="arithmetic_mean",
        size="arithmetic_mean",
        hover_name="local_site_name",
        hover_data={"city": True, "arithmetic_mean": True},
        title=f"Monitoring Sites for {selected_pollutant}",
        mapbox_style="open-street-map"
    )
    return fig

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
