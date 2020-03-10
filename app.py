import json
from datetime import datetime

import requests

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


API_KEY = 'e53638829bea94ae3a45213abb63a7ad'
FIELDS = [
    'swell.minBreakingHeight', 'swell.maxBreakingHeight', 'timestamp',
    'swell.components.*', 'wind.*', 'condition.temperature',
    'condition.weather', 'fadedRating', 'solidRating']

SPOTS = [{'label': str('Virginia Beach'), 'value': 396},
         {'label': str('S-Turns'), 'value': 398}]

app = dash.Dash()
server = app.server
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    dcc.Dropdown(id='spot-picker',
                options=[{'label': i['label'], 'value': i['value']} for i in SPOTS],
                value=396,
                clearable=False
    ),
    html.Div(id='forecast-graph'),
], style={'align': 'center'})

@app.callback(Output('forecast-graph', 'children'), [Input('spot-picker', 'value')])
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
                    x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                    y=[f['swell']['components']['primary']['height'] if f['swell']['components'].get('primary') else 'null' for f in response],
                    customdata=response,
                    mode='lines+markers',
                    name='primary'
                ),
                # secondary
                go.Scatter(
                    x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                    y=[f['swell']['components']['secondary']['height'] if f['swell']['components'].get('secondary') else 'null' for f in response],
                    customdata=response,
                    mode='lines+markers',
                    name='secondary'
                ),
                # tertiary
                go.Scatter(
                    x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                    y=[f['swell']['components']['tertiary']['height'] if f['swell']['components'].get('tertiary') else 'null' for f in response],
                    customdata=response,
                    mode='lines+markers',
                    name='tertiary'
                )
            ],
            'layout': go.Layout(
                title='5 Day Surf Forecast',
                yaxis={'title': 'Wave Height (ft)'},
                hovermode='closest',
            )
    }
    return dcc.Graph(id='forecast', figure=graph, config={'displayModeBar': False})

if __name__ == '__main__':
    app.run_server()