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
FIELDS = ['timestamp', 'swell.components.primary.height']
SPOTS = [{'label': str('Virginia Beach'), 'value': 396},
         {'label': str('S-Turns'), 'value': 398}]

app = dash.Dash()
server = app.server


def call_api(selected_spot):
    response = requests.get(
        'http://magicseaweed.com/api/{}/forecast/?spot_id={}&units={}&fields={}' \
            .format(API_KEY, selected_spot, "us", ','.join(FIELDS))).json()
    return pd.json_normalize(response)

df = call_api(396)

app.layout = html.Div([
    dcc.Dropdown(
        id='spot-picker',
        options=[{'label': i['label'], 'value': i['value']} for i in SPOTS],
        value=396,
        clearable=False,
        style={'display': 'inline-block', 'width': '75%'}
    ),
    dcc.DatePickerRange(
        id='date-picker',
        start_date=datetime.fromtimestamp(df['timestamp'].min()).strftime('%Y-%m-%d'),
        end_date=datetime.fromtimestamp(df['timestamp'].max()).strftime('%Y-%m-%d'),
        min_date_allowed=datetime.fromtimestamp(df['timestamp'].min()).strftime('%Y-%m-%d'),
        max_date_allowed=datetime.fromtimestamp(df['timestamp'].max()).strftime('%Y-%m-%d'),
        style={'display': 'inline-block', 'width': '25%'}
    ),
    dcc.Graph(
        id='forecast-graph',
        config={'displayModeBar': False}
    ),
    
], style={'align': 'center'})


@app.callback(Output('forecast-graph', 'figure'), 
                [Input('spot-picker', 'value'),
                 Input('date-picker', 'start_date'), 
                 Input('date-picker','end_date')
                ])
def update_figure(selected_spot, start_date, end_date):
    df = call_api(selected_spot)
    start_date = df['timestamp'] > datetime.strptime(start_date, '%Y-%m-%d').timestamp()
    end_date = df['timestamp'] < datetime.strptime(end_date, '%Y-%m-%d').timestamp()
    figure = {
                'data': [
                    # primary
                    go.Scatter(
                        x=[datetime.fromtimestamp(f) for f in df[start_date & end_date]['timestamp']],
                        y=df[start_date & end_date]['swell.components.primary.height'],
                        mode='lines+markers',
                        name='primary swell'
                    )
                ],
                'layout': go.Layout(
                    title='5 Day Surf Forecast',
                    yaxis={'title': 'Wave Height (ft)'},
                    hovermode='closest',
                )
            }
    return figure


if __name__ == '__main__':
    app.run_server()