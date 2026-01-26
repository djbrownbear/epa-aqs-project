import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json
import os

# added to handle relative path for JSON file
# replace with your desired file path
csv_filename = os.path.join(os.path.dirname(__file__), "my_reports", "combined_data_20251006.csv")
json_filename = os.path.join(os.path.dirname(__file__), "..", "assets", "air_quality_data.json")

# Load data from specified JSON file
with open(csv_filename, "r") as file:
    dtypes = {
        "latitude": float,
        "longitude": float,
        "arithmetic_mean": float,
        "date": str,
        "first_max_datetime": str,
        "parameter": str,
        "local_site_name": str,
        "state": str,
        "county": str,
        "city": str,
        "units_of_measure": str
    }
    data = pd.read_csv(file, dtype=dtypes).to_dict(orient="records")

with open(json_filename, "r") as f:
 json_data = json.load(f)

try:
    data_section = json_data.get("Data", [])
except KeyError:
    data_section = []
    print("Key 'Data' not found in JSON file.")

if data_section:
    df = pd.DataFrame(data_section)
else:
    df = pd.DataFrame(data)

df['date'] = pd.to_datetime(df['date'])
print(df["arithmetic_mean"].isna().sum())
df.dropna(subset=["arithmetic_mean"], inplace=True)

print(f"DataFrame columns: {df.columns}")

grouped_df = df.groupby(['date','county','parameter']).agg({
    'arithmetic_mean': 'mean',
    'local_site_name': 'first',
    'city': 'first',
    'state': 'first',
    'county_code': 'first',
    'latitude': 'first',
    'longitude': 'first',
    'units_of_measure': 'first'
}).reset_index()
print(f"Grouped DataFrame columns: {grouped_df.columns}")

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
    filtered_df = grouped_df[grouped_df["parameter"] == selected_pollutant]
    fig = px.line(
        filtered_df,
        x="date",
        y="arithmetic_mean",
        color="county",  # Example size mapping, adjust as needed
        title=f"{selected_pollutant} Levels Over Time",
        labels={"date": "Date", "arithmetic_mean": "Pollutant Level"},
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
    print(filtered_df['arithmetic_mean'])
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
