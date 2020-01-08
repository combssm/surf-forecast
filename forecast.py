from flask import Flask, render_template
from plotly.offline import plot
from plotly.graph_objs import Scatter
import requests
import time

app = Flask(__name__)

@app.route('/')
def home():
    """Displays main page"""
    try:
        response = requests.get('http://magicseaweed.com/api/e53638829bea94ae3a45213abb63a7ad/forecast/?spot_id=398').json()
    except Exception as e:
        return "<h2>Unable to retrieve swell data: {}</h2>".format(e)

    fdata = []
    for i in response:
        t = i['timestamp']
        sminh = i['swell']['minBreakingHeight']
        smaxh = i['swell']['maxBreakingHeight']
        sh = i['swell']['components']['primary']['height']
        sd = i['swell']['components']['primary']['compassDirection']
        ws = i['wind']['speed']
        wd = i['wind']['compassDirection']
        fdata.append({
            "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)),
            "swellminheight": sminh,
            "swellmaxheight": smaxh,
            "swellheight": sh,
            "swelldirection": sd,
            "windspeed": ws,
            "winddirection": wd
        })
    return render_template('index.html', fdata=fdata)

if __name__ == '__main__':
    app.run(debug=True)