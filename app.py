import json
from datetime import datetime
from dateutil.parser import parse

import requests

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd


API_KEY = 'e53638829bea94ae3a45213abb63a7ad'
FIELDS = ['timestamp', 'swell.components.*']
SPOTS = [{'label': str('Virginia Beach'), 'value': 396},
         {'label': str('S-Turns'), 'value': 398}]

app = dash.Dash(serve_locally = False)
server = app.server

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='spot-picker',
            options=[{'label': i['label'], 'value': i['value']} for i in SPOTS],
            value=396,
            clearable=False,
            style={'border': '3px solid orange'}
        )
    ], style={'border': '3px solid green'}),
    html.Div([
        dcc.Graph(
            id='forecast-graph',
            config={'displayModeBar': False},
        )
    ], style={'border': '3px solid green'}),
    html.Pre("Forecast Details",
        id='forecast-detail',
        style={'border': '3px solid red'}),   
], style={'width': '50%', 'margin': 'auto', 'padding': '20px', 'border': '3px solid blue'})


@app.callback(Output('forecast-graph', 'figure'),[Input('spot-picker', 'value')])
def update_figure(selected_spot):
    response = requests.get(
        'http://magicseaweed.com/api/{}/forecast/?spot_id={}&units={}&fields={}'.format(
            API_KEY,
            selected_spot,
            "us", 
            ','.join(FIELDS))).json()
    graph = {
            'data': [
                # primary
                go.Scatter(
                    x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                    y = [f['swell']['components']['primary']['height'] if f['swell']['components'].get('primary') else 'null' for f in response],
                    customdata=response,
                    mode = 'lines+markers',
                    name = 'primary'
                ),
                # secondary
                go.Scatter(
                    x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                    y = [f['swell']['components']['secondary']['height'] if f['swell']['components'].get('secondary') else 'null' for f in response],
                    customdata=response,
                    mode = 'lines+markers',
                    name = 'secondary'
                ),
                # tertiary
                go.Scatter(
                    x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                    y = [f['swell']['components']['tertiary']['height'] if f['swell']['components'].get('tertiary') else 'null' for f in response],
                    customdata=response,
                    mode = 'lines+markers',
                    name = 'tertiary'
                )
            ],
            'layout': go.Layout(
                title = '5 Day Surf Forecast',
                yaxis = {'title': 'Wave Height (ft)'},
                hovermode='closest',
            )
    }
    return graph

@app.callback(Output('forecast-detail','children'), [Input('forecast-graph', 'clickData')])
def update_forecast_detail(click_data):
    return json.dumps(click_data,indent=2)

if __name__ == '__main__':
    app.run_server()