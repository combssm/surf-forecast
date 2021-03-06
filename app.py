"""
Main file for surf forecast dash app
Read data from magic seaweed api and print to screen
"""
from datetime import datetime
import yaml
import requests
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


with open('config.yaml', 'r') as conf:
    config = yaml.load(conf, Loader=yaml.Loader)


app = dash.Dash(__name__)
server = app.server
app.title = 'Combsvb Surf Forecast'


def call_api(key, spot_id, units, fields, **kwargs):
    """
    Reach out magic seaweed api:
    @key: magic seaweed api key
    @spot_id: spot id (found via url)
    @units: english or metric
    @fields: specific data to retrieve from magic seaweed api
    """
    return requests.get(
        f'http://magicseaweed.com/api/{key}/forecast/?spot_id={spot_id}&units={units}&fields={fields}').json()


def serve_layout():
    """
    Build surf forecast visual and display
    """
    response = call_api(**config['api'])

    figure = {
        'data': [
            # primary
            go.Scatter(
                x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                y=[f['swell']['components']['primary']['height']
                    for f in response],
                mode='lines+markers',
                name='primary',
                customdata=response
            ),
            # secondary
            go.Scatter(
                x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                y=[f['swell']['components']['secondary']['height'] if f['swell']
                    ['components'].get('secondary') else 'asdfds' for f in response],
                mode='lines+markers',
                name='secondary',
                customdata=response
            ),
            # tertiary
            go.Scatter(
                x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                y=[f['swell']['components']['tertiary']['height'] if f['swell']
                    ['components'].get('tertiary') else 'sdfdsf' for f in response],
                mode='lines+markers',
                name='tertiary',
                customdata=response
            ),
            # swell.minBreakingHeight
            go.Bar(
                x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                y=[f['swell']['minBreakingHeight'] if f['swell'].get(
                    'minBreakingHeight') else 0 for f in response],
                name='Min. Breaking Height',
                marker=dict(color='#9EA0A1')
            ),
            # swell.maxBreakingHeight
            go.Bar(
                x=[datetime.fromtimestamp(f['timestamp']) for f in response],
                y=[f['swell']['maxBreakingHeight'] if f['swell'].get(
                    'maxBreakingHeight') else 0 for f in response],
                name='Min. Breaking Height',
                marker=dict(color='#FFD700')
            )
        ],
        'layout': go.Layout(
            title='5 Day Surf Forecast',
            yaxis={'title': 'Wave Height (ft)'},
            hovermode='closest',
        )
    }

    return html.Div(
        [
            html.Div(dcc.Graph(id='forecast-graph', figure=figure), style={
                     'box-shadow': '0 2px 10px #ccc', 'border': '1px solid #eee', 'width': '80%', 'margin': '5px'}),
            html.Div("Click on a point to see more details", id='forecast-detail', style={
                     'box-shadow': '0 2px 10px #ccc', 'border': '1px solid #eee', 'width': '25%', 'padding': '10px', 'margin': '5px', 'textAlign': 'left', 'backgroundColor': '#ffffff'})
        ], style={'display': 'inline-block', 'padding': '15px', 'width': '100%', 'textAlign': 'center'}
    )


# https://dash.plotly.com/live-updates
app.layout = serve_layout


@app.callback(Output('forecast-detail', 'children'), [Input('forecast-graph', 'clickData')])
def update_forecast_detail(clickData):
    """
    Ability to click on data point and get detailed forcast info
    Reference: https://dash.plotly.com/basic-callbacks
    """
    if not clickData:
        return "Click on a point to see more details"
    date = datetime.fromtimestamp(
        clickData['points'][0]['customdata']['timestamp'])
    if clickData['points'][0]['customdata']['swell']['minBreakingHeight'] == clickData['points'][0]['customdata']['swell']['maxBreakingHeight']:
        swell_size = "Swell Size      : {}".format(
            clickData['points'][0]['customdata']['swell']['minBreakingHeight'])
    else:
        swell_size = "Swell Size      : {}".format(str(clickData['points'][0]['customdata']['swell']['minBreakingHeight']) + " - " + str(
            clickData['points'][0]['customdata']['swell']['maxBreakingHeight']))
    primary_swell = "Primary Swell   : {points[0][customdata][swell][components][primary][height]}ft @ {points[0][customdata][swell][components][primary][period]}s {points[0][customdata][swell][components][primary][compassDirection]}".format(
        **clickData)
    if not clickData['points'][0]['customdata']['swell']['components'].get('secondary'):
        secondary_swell = "Secondary Swell :"
    else:
        secondary_swell = "Secondary Swell : {points[0][customdata][swell][components][secondary][height]}ft @ {points[0][customdata][swell][components][secondary][period]}s {points[0][customdata][swell][components][secondary][compassDirection]}".format(
            **clickData)
    if not clickData['points'][0]['customdata']['swell']['components'].get('tertiary'):
        tertiary_swell = "Tertiary Swell  :"
    else:
        tertiary_swell = "Tertiary Swell  : {points[0][customdata][swell][components][tertiary][height]}ft @ {points[0][customdata][swell][components][tertiary][period]}s {points[0][customdata][swell][components][tertiary][compassDirection]}".format(
            **clickData)
    wind_condition = "Wind Condition  : {points[0][customdata][wind][speed]}mph {points[0][customdata][wind][compassDirection]}".format(
        **clickData)
    temperature = "Temperature     : {points[0][customdata][condition][temperature]}F".format(
        **clickData)
    return html.Pre("""Forecast Details: {}
{}ft
{}
{}
{}
{}
{}""".format(date, swell_size, primary_swell, secondary_swell, tertiary_swell, wind_condition, temperature))


if __name__ == '__main__':
    app.run_server()
