import re
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from pathlib import Path
from plotly import graph_objects as go

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

data_path = Path("data/combined_data_20251006.csv")
filename = data_path.name

# Load your dataset
df = pd.read_csv(data_path)

# Basic preprocessing (adjust column names as needed)
df['date'] = pd.to_datetime(df['date'])
df.dropna(subset=["arithmetic_mean"], inplace=True)

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

df_5_rows = grouped_df.head()
csv_string = df_5_rows.to_csv(index=False)

# Path to cleaned data for LLM context
cleaned_data_path = Path("data/cleaned_combined_data_20251006.csv")
filename = cleaned_data_path.name

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You're a data visualization expert and use your favorite graphing library Plotly only. Suppose, that"
     "the data is provided as a {filename} file. Here are the first 5 rows of the data set: {data}"
     "Follow the user's instructions carefully and provide only the code as output. Do not include any explanations or additional text."
    ),
    MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | llm

def get_fig_from_code(code):
    local_vars = {}
    exec(code, {}, local_vars)
    return local_vars.get('fig', None)

def get_param_options(param=None, add_all=True, dataframe=df):
    param_options = [{'label': str(p), 'value': p} for p in sorted(dataframe[str(param)].unique())]
    if add_all:
        param_options.insert(0, {'label': 'All', 'value': 'all'})
    return param_options

county_options = get_param_options('county')
pollutant_options = get_param_options('parameter', add_all=False)

app = dash.Dash(__name__)
server = app.server # Expose the server variable for deployments
app.title = "Air Quality Dashboard"

app.layout = html.Div([
    html.H1("Air Quality Data Dashboard"),
    html.H2("Using Gemini-2.5 to Generate Visualizations from Natural Language"),
    html.P("Interactively explore air quality data and generate custom visualizations using natural language."),
    dcc.Textarea(id='user-input', placeholder='Enter your graph request here...', style={'width': '100%'}),
    html.Button('Submit', id='submit-button'),
    dcc.Loading(
        [html.Div(id='output-div'), dcc.Markdown(id='generated-code')
         ], type="cube"),

    html.Br(),
    html.H2("Predefined Visualizations"),
    html.P("Explore predefined visualizations of the air quality dataset."),
    html.Label("Select County:"),
    dcc.Dropdown(
        id='county-dropdown',
        options=county_options,
        value=None,
        multi=True,
        clearable=True
    ),
    html.Label("Select Pollutant:"),
    dcc.Dropdown(
        id='pollutant-dropdown',
        options=[{'label': str(p), 'value': p} for p in sorted(df['parameter'].unique())],
        value=df['parameter'].unique()[0],
        multi=False,
        clearable=False
    ),
    dcc.Graph(id='time-series-plot'),
    dcc.Graph(id='distribution-plot'),
    dcc.Graph(id='map-plot')
])

@app.callback(
    Output('county-dropdown', 'value'),
    [Input('county-dropdown', 'value')],
    [State('county-dropdown', 'options')]
)
def clear_county_selection(selected_county, options):
    if selected_county and 'all' not in selected_county:
        return [c for c in selected_county]
    return []

@app.callback(
    Output('county-dropdown', 'options'),
    [Input('pollutant-dropdown', 'value')],
    [State('county-dropdown', 'options')]
)
def set_county_options(selected_pollutant, options):
    if not selected_pollutant or 'all' in selected_pollutant:
        # If "All Pollutants" is selected, show all counties
        return get_param_options('county', add_all=False)
    else:
        # Filter pollutants based on selected counties
        filtered = df[df['parameter'] == selected_pollutant]
        return get_param_options('county', add_all=True, dataframe=filtered)

@app.callback(
    Output('time-series-plot', 'figure'),
    [Input('pollutant-dropdown', 'value')],
    [Input('county-dropdown', 'value')]
)
def update_time_series(selected_pollutant, selected_county):
    # Handle "All Counties" selection
    if not selected_county or selected_county[0] == 'all':
        filtered = grouped_df[grouped_df['parameter'] == selected_pollutant]
        fig = px.line(
            filtered,
            x='date',
            y='arithmetic_mean',
            color='county',
            title="Sample Measurement Over Time (All Counties)"
        )
        return fig
    else:
        if isinstance(selected_county, str):
            selected_county = [selected_county]

        filtered = grouped_df[grouped_df['county'].isin(selected_county) & (grouped_df['parameter'] == selected_pollutant)]
        fig = px.line(
            filtered,
            x='date',
            y='arithmetic_mean',
            color='county',
            title=f"Sample Measurement Over Time (Count{'ies' if len(selected_county) > 1 else 'y'}: {', '.join(selected_county)})"
        )
        return fig

@app.callback(
    Output('distribution-plot', 'figure'),
    [Input('county-dropdown', 'value')]
)
def update_distribution(selected_county):
    if not selected_county or selected_county[0] == 'all':
        filtered = df
        fig = px.histogram(
            filtered,
            x='arithmetic_mean',
            nbins=50,
            title="Distribution of Sample Measurement (All Counties)"
        )
        return fig
    else:
        filtered = df[df['county'].isin(selected_county)]
        fig = px.histogram(
            filtered,
            x='arithmetic_mean',
            nbins=50,
            title=f"Distribution of Sample Measurement (Count{'ies' if len(selected_county) > 1 else 'y'}: {', '.join(selected_county)})"
        )
        return fig

@app.callback(
    Output('map-plot', 'figure'),
    [Input('pollutant-dropdown', 'value')]
)
def update_map(selected_pollutant):
    filtered = df[df['parameter'] == selected_pollutant].copy()
    size_col = 'arithmetic_mean'

    # If any values in size_col are negative, disable sizing
    if (filtered[size_col] < 0).any() or filtered[size_col].isnull().all():
        size_col = None

    fig = px.scatter_mapbox(
        filtered,
        lat='latitude',
        lon='longitude',
        color='arithmetic_mean',  # or another measurement column
        size=size_col,
        hover_name='local_site_name',
        hover_data=['arithmetic_mean', 'date'],
        zoom=8,
        mapbox_style="open-street-map",
        title=f"Air Quality Measurements (Pollutant {selected_pollutant})"
    )
    return fig

@app.callback(
    Output('output-div', 'children'),
    Output('generated-code', 'children'),
    Input('submit-button', 'n_clicks'),
    State('user-input', 'value'),
    prevent_initial_call=True
)
def create_graph(_, user_input):
    response = chain.invoke({
        "messages": [HumanMessage(content=user_input)],
        "data": csv_string,
        "dataframe": 'cleaned_df'
    })
    res_output = response.content
    print("Generated Code:\n", res_output)

    # check if the answer includes code. This regular expression matches code blocks
    # with or without language specifier (like `python`)
    code_block_pattern = r"```(?:[Pp]ython)?\s*(.*?)```"
    match = re.search(code_block_pattern, res_output, re.DOTALL)
    print("Match:", match.group(1))

    if match:
        code_block = match.group(1).strip()
        cleaned_code = re.sub(r'(?m)^\s*fig\.show\(\)\s*$', '', code_block)
        fig = get_fig_from_code(cleaned_code)
        if fig:
            return dcc.Graph(figure=fig), res_output
        else:
            return "Error generating figure from code.", f"```python\n{cleaned_code}\n```"
    else:
        return "No code block found in the response.", res_output

if __name__ == '__main__':
    app.run(debug=True)