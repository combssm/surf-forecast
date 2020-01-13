from flask import Flask, render_template
import requests
import time

API_KEY = 'e53638829bea94ae3a45213abb63a7ad'
FIELDS = [
    'swell.minBreakingHeight', 'swell.maxBreakingHeight', 'timestamp',
    'swell.components.primary.*', 'wind.*,condition.temperature']

app = Flask(__name__)

class Forecast:
    """
    Class to hold all forecast data for a given timestamp
    data: dictionary containing all forecast data from API
    """
    def __init__(self, data):
        self.timestamp = time.strftime('%a %_m/%d %l:%M%P', time.localtime(data['timestamp']))
        self.min_swell_height = data['swell']['minBreakingHeight']
        self.max_swell_height = data['swell']['maxBreakingHeight']
        self.swell_direction = data['swell']['components']['primary']['compassDirection']
        self.wind_direction = data['wind']['compassDirection']
        self.wind_speed = data['wind']['speed']
        self.temperature = data['condition']['temperature']


@app.route('/')
def home():
    """Displays main page"""
    try:
        s_turns_response = requests.get(
            'http://magicseaweed.com/api/{}/forecast/?spot_id={}&units={}&fields={}'.format(
                API_KEY,
                "398", # S-Turns
                "us", 
                ','.join(FIELDS))
            ).json()
        vb_response = requests.get(
            'http://magicseaweed.com/api/{}/forecast/?spot_id={}&units={}&fields={}'.format(
                API_KEY,
                "396", # Virginia Beach
                "us", 
                ','.join(FIELDS))
            ).json()
    except Exception as e:
        return "<h2>Unable to retrieve swell data: {}</h2>".format(e)

    s_turns_fdata, vb_fdata = [], []
    for i in s_turns_response:
        f = Forecast(i)
        s_turns_fdata.append(f)
    for i in vb_response:
        f = Forecast(i)
        vb_fdata.append(f)

    return render_template('index.html', s_turns_fdata=s_turns_fdata, vb_fdata=vb_fdata)


if __name__ == '__main__':
    app.run(debug=True)
