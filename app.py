import json
from datetime import datetime
from dateutil.parser import parse

import requests

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


API_KEY = 'e53638829bea94ae3a45213abb63a7ad'
FIELDS = ['timestamp', 'swell.components.primary.height', 'swell.components.secondary.height', 'swell.components.tertiary.height']
SPOTS = [{'label': str('Virginia Beach'), 'value': 396},
         {'label': str('S-Turns'), 'value': 398}]

app = dash.Dash()
server = app.server

response = requests.get(
    'http://magicseaweed.com/api/{}/forecast/?spot_id={}&units={}&fields={}'.format(
        API_KEY,
        396,
        "us", 
        ','.join(FIELDS))).json()

figure = {
        'data': [
            # primary
            go.Scatter(
                x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                y = [f['swell']['components']['primary']['height'] for f in response],
                mode = 'lines+markers',
                name = 'primary'
            ),
            # secondary
            go.Scatter(
                x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                y = [f['swell']['components']['secondary']['height'] if f['swell']['components'].get('secondary') else 'asdfds' for f in response],
                mode = 'lines+markers',
                name = 'secondary'
            ),
            # tertiary
            go.Scatter(
                x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                y = [f['swell']['components']['tertiary']['height'] if f['swell']['components'].get('tertiary') else 'sdfdsf' for f in response],
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

app.layout = html.Div(
    [
        html.Div(dcc.Graph(id='forecast-graph', figure=figure), style={'border': '3px solid black', 'width': '66%'}),
        html.Div("Some Text", id='forecast-detail', style={'border': '3px solid black', 'width': '34%'})
    ], style={'display': 'inline-block', 'padding': '15px'}
)

if __name__ == '__main__':
    app.run_server()