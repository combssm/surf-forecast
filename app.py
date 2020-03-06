import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import plotly.graph_objs as go
import time
from datetime import datetime
import json

API_KEY = 'e53638829bea94ae3a45213abb63a7ad'
FIELDS = [
    'swell.minBreakingHeight', 'swell.maxBreakingHeight', 'timestamp',
    'swell.components.*', 'wind.*', 'condition.temperature',
    'condition.weather', 'fadedRating', 'solidRating']

app = dash.Dash()
server = app.server

try:
    response = requests.get(
        'http://magicseaweed.com/api/{}/forecast/?spot_id={}&units={}&fields={}'.format(
            API_KEY,
            "396", # Virginia Beach
            "us", 
            ','.join(FIELDS))
        ).json()
except Exception as e:
    print("<h2>Unable to retrieve swell data: {}</h2>".format(e))

app.layout = html.Div([
    dcc.Graph(
        id='surf-forecast',
        figure={
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
                # secondary
                go.Scatter(
                    x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                    y = [f['swell']['components']['tertiary']['height'] if f['swell']['components'].get('tertiary') else 'null' for f in response],
                    customdata=response,
                    mode = 'lines+markers',
                    name = 'tertiary'
                )
            ],
            'layout': go.Layout(
                title = '5 Day Virginia Beach Surf Forecast',
                xaxis = {'title': 'Date'},
                yaxis = {'title': 'Wave Height (ft)'},
                hovermode='closest'
            )
        }
    ),
    html.Div([
        html.H1(id='date'),
        html.H2(id='swell-size'),
        html.H2(id='wind-speed')
    ]),
    html.Pre(id='hover-data', style={'paddingTop':35})
])

# TODO: Set Default Values for elements
# TODO: Multiple Outputs
# TODO: Update Forecast-detail on Click
# TODO: Customize Data in Hoverbox

@app.callback(Output('date', 'children'), [Input('surf-forecast', 'hoverData')])
def update_date(hoverData):
    date = datetime.fromtimestamp(hoverData['points'][0]['customdata']['timestamp'])
    return date


@app.callback(Output('swell-size', 'children'), [Input('surf-forecast', 'hoverData')])
def update_swell_size(hoverData):
    min = hoverData['points'][0]['customdata']['swell']['minBreakingHeight']
    max = hoverData['points'][0]['customdata']['swell']['maxBreakingHeight']
    if min == max:
        swell = "{}ft".format(min)
    else:
        swell = "{}-{}ft".format(min, max)
    return swell


@app.callback(Output('wind-speed', 'children'), [Input('surf-forecast', 'hoverData')])
def update_swell_size(hoverData):
    speed = hoverData['points'][0]['customdata']['wind']['speed']
    direction = hoverData['points'][0]['customdata']['wind']['compassDirection']
    wind = "{}mph {}".format(speed, direction)
    return wind


@app.callback(Output('hover-data', 'children'), [Input('surf-forecast', 'hoverData')])
def update_hoverdata(hoverData):
    return json.dumps(hoverData, indent=2)

if __name__ == '__main__':
    app.run_server()