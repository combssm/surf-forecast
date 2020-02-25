from flask import Flask, render_template
import requests
import time
from plotly.graph_objs import Scatter
from plotly.offline import plot
from datetime import datetime

API_KEY = 'e53638829bea94ae3a45213abb63a7ad'
FIELDS = [
    'swell.minBreakingHeight', 'swell.maxBreakingHeight', 'timestamp',
    'swell.components.primary.*', 'wind.*', 'condition.temperature',
    'condition.weather', 'fadedRating', 'solidRating']

app = Flask(__name__)

class Forecast:
    """
    Class to hold all forecast data for a given timestamp
    data: dictionary containing all forecast data from API
    """
    def __init__(self, data):
        self.timestamp = data['timestamp']
        self.hour = time.strftime('%l%P', time.localtime(data['timestamp']))
        self.min_swell_height = data['swell']['minBreakingHeight']
        self.max_swell_height = data['swell']['maxBreakingHeight']
        self.swell_direction = data['swell']['components']['primary']['compassDirection']
        self.primary_height = data['swell']['components']['primary']['height']
        self.wind_direction = data['wind']['compassDirection']
        self.wind_speed = data['wind']['speed']
        self.temperature = data['condition']['temperature']
        self.weather_condition = data['condition']['weather']
        self.faded_rating = data['fadedRating']
        self.solid_rating = data['solidRating']
        self.day = time.strftime('%A %_m/%d', time.localtime(data['timestamp']))


@app.route('/')
def home():
    """Displays main page"""
    try:
        response = requests.get(
            'http://magicseaweed.com/api/{}/forecast/?spot_id={}&units={}&fields={}'.format(
                API_KEY,
                "396", # Virginia Beach
                "us", 
                ','.join(FIELDS))
            ).json()
    except Exception as e:
        return "<h2>Unable to retrieve swell data: {}</h2>".format(e)

    fdata = {}
    x = []
    y = []
    for i in response:
        f = Forecast(i)
        x.append(datetime.fromtimestamp(f.timestamp))
        y.append(f.primary_height)
        if fdata.get(f.day) == None:
            fdata[f.day] = []
        fdata[f.day].append(f)

    my_plot_div = plot([Scatter(x=x, y=y)], output_type='div', "layout": {"title": {"text": "A Bar Chart"}})

    return render_template('index.html', fdata=fdata, my_plot_div=my_plot_div)


if __name__ == '__main__':
    app.run(debug=True)
