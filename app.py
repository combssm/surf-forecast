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
    'swell.components.primary.*', 'wind.*', 'condition.temperature',
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
                    y = [f['swell']['components']['primary']['height'] for f in response],
                    customdata=[{
                        'temp': t['condition']['temperature'],
                        'solidRating': t['solidRating'],
                        'wind_speed': t['wind']['speed'],
                        'wind_direction': t['wind']['direction'],
                        'wind_compass_direction': t['wind']['compassDirection']}
                         for t in response],
                    mode = 'lines+markers',
                    name = 'primary'
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
    html.Pre(id='hover-data', style={'paddingTop':35})
])

@app.callback(Output('hover-data', 'children'), [Input('surf-forecast', 'hoverData')])
def update_hoverdata(hoverData):
    return json.dumps(hoverData, indent=2)

if __name__ == '__main__':
    app.run_server()