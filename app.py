import json
from datetime import datetime

import requests

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

# TODO: Set Default Values for elements
# TODO: Multiple Outputs
# TODO: Update Forecast-detail on Click
# TODO: Customize Data in Hoverbox


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
                title = '5 Day Virginia Beach Surf Forecast',
                yaxis = {'title': 'Wave Height (ft)'},
                hovermode='closest',
                #plot_bgcolor='aliceblue',
                #paper_bgcolor='#0079c4'
            )
        }
    ),
    html.Div(id='forecast-table'),
    html.Pre(id='hover-data', style={'paddingTop':35})
], style={'align': 'center'})


@app.callback(Output('forecast-table', 'children'), [Input('surf-forecast', 'hoverData')])
def update_forecast_table(hoverData):
    if not hoverData:
        return "Hover over a point"

    # Generate swell size format string
    min = hoverData['points'][0]['customdata']['swell']['minBreakingHeight']
    max = hoverData['points'][0]['customdata']['swell']['maxBreakingHeight']
    if min == max:
        swell_size = "{}ft".format(min)
    else:
        swell_size = "{}-{}ft".format(min, max)

    # Generate wind speed format string
    speed = hoverData['points'][0]['customdata']['wind']['speed']
    direction = hoverData['points'][0]['customdata']['wind']['compassDirection']
    wind = "{}mph {}".format(speed, direction)

    # Generate swell stats
    primary_swell = str(hoverData['points'][0]['customdata']['swell']['components']['primary']['height']) + " " + \
                str(hoverData['points'][0]['customdata']['swell']['components']['primary']['compassDirection']) + " @ " + \
                str(hoverData['points'][0]['customdata']['swell']['components']['primary']['period']) + "s"

    try:
        secondary_swell = str(hoverData['points'][0]['customdata']['swell']['components']['secondary']['height']) + " " + \
                        str(hoverData['points'][0]['customdata']['swell']['components']['secondary']['compassDirection']) + " @ " + \
                        str(hoverData['points'][0]['customdata']['swell']['components']['secondary']['period']) + "s"
    except Exception:
        secondary_swell = ""
    try:
        tertiary_swell = str(hoverData['points'][0]['customdata']['swell']['components']['tertiary']['height']) + " " + \
                        str(hoverData['points'][0]['customdata']['swell']['components']['tertiary']['compassDirection']) + " @ " + \
                        str(hoverData['points'][0]['customdata']['swell']['components']['tertiary']['period']) + "s"                
    except Exception:
        tertiary_swell = ""

    table = html.Table([
        # Date Header
        html.Thead(
            datetime.strftime(
                datetime.fromtimestamp(
                    hoverData['points'][0]['customdata']['timestamp']), 
                    "%B %d, %Y %I:%M%p"
                    ), style={'textAlign': 'center'}
                ),
        # Column Headers
        html.Tr([
            html.Td("Swell Data"),
            html.Td("Tide Data"),
            html.Td("Weather Data")
        ]),
        html.Tr([
            html.Td("Swell Size: {}".format(swell_size)),
            html.Td("High Tides: {}/{}".format("TBD", "TBD")),
            html.Td("Wind: {}".format(wind))
        ]),
        html.Tr([
            html.Td("Primary Swell: {}".format(primary_swell)),
            html.Td("Low Tides: {}/{}".format("TBD", "TBD")),
            html.Td("Temperature: {}".format(hoverData['points'][0]['customdata']['condition']['temperature']))
        ]),
        html.Tr([
            html.Td("Secondary Swell: {}".format(secondary_swell)),
            html.Td(""),
            html.Td("Feels Like: {}".format(hoverData['points'][0]['customdata']['wind']['chill']))
        ]),
        html.Tr([
            html.Td("Tertiary Swell: {}".format(tertiary_swell)),
            html.Td(""),
            html.Td("Weather: {}".format(hoverData['points'][0]['customdata']['condition']['weather']))
        ])
    ], style={'border': '1px solid black'})
    return table

@app.callback(Output('hover-data', 'children'), [Input('surf-forecast', 'hoverData')])
def update_hoverdata(hoverData):
    return json.dumps(hoverData, indent=2)

if __name__ == '__main__':
    app.run_server()