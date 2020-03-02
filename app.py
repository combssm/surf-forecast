import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
import plotly.graph_objs as go
import time

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
                    x = [f['timestamp'] for f in response],
                    y = [f['swell']['components']['primary']['height'] for f in response],
                    mode = 'lines+markers',
                    name = 'primary'
                )
            ],
            'layout': go.Layout(
                title = 'Surf Forecast',
                xaxis = {'title': 'Date'},
                yaxis = {'title': 'Wave Height'},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server()