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
FIELDS = ['timestamp', 'swell.*', 'wind.*', 'condition.temperature']
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
                name = 'primary',
                customdata=response
            ),
            # secondary
            go.Scatter(
                x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                y = [f['swell']['components']['secondary']['height'] if f['swell']['components'].get('secondary') else 'asdfds' for f in response],
                mode = 'lines+markers',
                name = 'secondary',
                customdata=response
            ),
            # tertiary
            go.Scatter(
                x = [datetime.fromtimestamp(f['timestamp']) for f in response],
                y = [f['swell']['components']['tertiary']['height'] if f['swell']['components'].get('tertiary') else 'sdfdsf' for f in response],
                mode = 'lines+markers',
                name = 'tertiary',
                customdata=response
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
        html.Div(dcc.Graph(id='forecast-graph', figure=figure), style={'border': '3px solid black', 'float': 'left', 'width': '56%'}),
        html.Div("Forecast Details:", id='forecast-detail', style={'border': '3px solid black', 'float': 'left', 'width': '24%', 'padding': '10px'})
    ], style={'display': 'inline-block', 'padding': '15px', 'width': '100%', 'border': '3px solid black'}
)

@app.callback(Output('forecast-detail', 'children'), [Input('forecast-graph', 'hoverData')])
def update_forecast_detail(hoverData):
    date = datetime.fromtimestamp(hoverData['points'][0]['customdata']['timestamp'])
    primary_swell =       "Primary Swell   : {points[0][customdata][swell][components][primary][height]}ft @ {points[0][customdata][swell][components][primary][period]}s {points[0][customdata][swell][components][primary][compassDirection]}".format(**hoverData)
    if not hoverData['points'][0]['customdata']['swell']['components'].get('secondary'):
        secondary_swell = "Secondary Swell :"
    else:
        secondary_swell = "Secondary Swell : {points[0][customdata][swell][components][secondary][height]}ft @ {points[0][customdata][swell][components][secondary][period]}s {points[0][customdata][swell][components][secondary][compassDirection]}".format(**hoverData)
    if not hoverData['points'][0]['customdata']['swell']['components'].get('tertiary'):
        tertiary_swell =  "Tertiary Swell  :"
    else:
        tertiary_swell =  "Tertiary Swell  : {points[0][customdata][swell][components][tertiary][height]}ft @ {points[0][customdata][swell][components][tertiary][period]}s {points[0][customdata][swell][components][tertiary][compassDirection]}".format(**hoverData)
    wind_condition =      "Wind Condition  : {points[0][customdata][wind][speed]}mph {points[0][customdata][wind][compassDirection]}".format(**hoverData)
    temperature =         "Temperature     : {points[0][customdata][condition][temperature]}F".format(**hoverData)
    return html.Pre(    """Forecast Details: {}
{}
{}
{}
{}
{}""".format(date, primary_swell, secondary_swell, tertiary_swell, wind_condition, temperature))


if __name__ == '__main__':
    app.run_server()
