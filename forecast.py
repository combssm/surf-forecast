from flask import Flask, render_template
import requests
import time
from plotly.offline import plot
from plotly.graph_objs import Scatter

app = Flask(__name__)

class Forecast:
    """
    Class to hold all forecast data for a given timestamp
    data: dictionary containing all forecast data from API
    """
    def __init__(self, data):
        self.timestamp = data['timestamp']
        self.min_swell_height = data['swell']['minBreakingHeight']
        self.max_swell_height = data['swell']['maxBreakingHeight']
        self.swell_direction = data['swell']['components']['primary']['compassDirection']
        self.wind_direction = data['wind']['compassDirection']
        self.wind_speed = data['wind']['speed']


@app.route('/')
def home():
    """Displays main page"""
    try:
        response = requests.get('http://magicseaweed.com/api/e53638829bea94ae3a45213abb63a7ad/forecast/?spot_id=398&units=us').json()
    except Exception as e:
        return "<h2>Unable to retrieve swell data: {}</h2>".format(e)

    fdata = []
    for i in response:
        f = Forecast(i)
        fdata.append(f)

    graph = plot([Scatter(x=[x.timestamp for x in fdata], y=[y.max_swell_height for y in fdata])], output_type='div')    
    return render_template('index.html', fdata=fdata, graph=graph)

if __name__ == '__main__':
    app.run(debug=True)