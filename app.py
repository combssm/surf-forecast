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
    html.Div([
        html.Table([
            html.Tr(
                html.Td(id='date',colSpan='3',style={'textAlign': 'center'})
            ),
            html.Tr([
                html.Td(id='swell-data', style={'width': '33%'}),
                html.Td(id='tide-data', style={'width': '33%'}),
                html.Td(id='weather-data', style={'width': '33%'})
            ])
        ], style={'border': '1px solid black',
                  'width': '50%',
                  'display': 'block',
                  'margin-left': 'auto',
                  'margin-right': 'auto',
                  })
    ]),
    html.Pre(id='fake-forecast', style={'paddingTop':35}),
    html.Pre(id='hover-data', style={'paddingTop':35})
], style={'align': 'center'})


# TODO: Set Default Values for elements
# TODO: Multiple Outputs
# TODO: Update Forecast-detail on Click
# TODO: Customize Data in Hoverbox

@app.callback(Output('date', 'children'), [Input('surf-forecast', 'hoverData')])
def update_date(hoverData):
    date = datetime.fromtimestamp(hoverData['points'][0]['customdata']['timestamp'])
    return datetime.strftime(date, "%B %d, %Y %I:%M%p")


@app.callback(Output('swell-data', 'children'), [Input('surf-forecast', 'hoverData')])
def update_swell_size(hoverData):
    min = hoverData['points'][0]['customdata']['swell']['minBreakingHeight']
    max = hoverData['points'][0]['customdata']['swell']['maxBreakingHeight']
    if min == max:
        swell_size = "{}ft".format(min)
    else:
        swell_size = "{}-{}ft".format(min, max)

    primary_swell = str(hoverData['points'][0]['customdata']['swell']['components']['primary']['height']) + " " + \
                    str(hoverData['points'][0]['customdata']['swell']['components']['primary']['compassDirection']) + " @ " + \
                    str(hoverData['points'][0]['customdata']['swell']['components']['primary']['period']) + "s"

    return html.Pre("""Swell Info
Size:      {}
Primary:   {}
Secondary: {}
Tertiary:  {}""".format(swell_size, primary_swell, "1.3 ESE", "1.2 SSW"))


@app.callback(Output('weather-data', 'children'), [Input('surf-forecast', 'hoverData')])
def update_wind_size(hoverData):
    speed = hoverData['points'][0]['customdata']['wind']['speed']
    direction = hoverData['points'][0]['customdata']['wind']['compassDirection']
    wind = "{}mph {}".format(speed, direction)
    return wind


@app.callback(Output('fake-forecast', 'children'), [Input('surf-forecast', 'hoverData')])
def update_fake_forecast(hoverData):
    fake_forecast = '''|----------------------------------------------------------------------------------------------|
|                                     March 07, 2020 TIME?                                     |
|  Swell                                    Tides                           Weather            |
|  Size:      2-3 ft              Low:    3:00am/3:30pm                 Wind:        8 mph SW  |
|  Primary:   4.5 ENE             High:   9:00am/9:45pm                 Temperature: 61F       |
|  Secondary: 3.1 SSW                                                   Feels Like:  54F       |
|  Tertiary:  0.2 SE                                                    Condition:   Cloudy    |
|----------------------------------------------------------------------------------------------|
'''
    return fake_forecast


@app.callback(Output('hover-data', 'children'), [Input('surf-forecast', 'hoverData')])
def update_hoverdata(hoverData):
    return json.dumps(hoverData, indent=2)

if __name__ == '__main__':
    app.run_server()