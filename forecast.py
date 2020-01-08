from flask import Flask, render_template
from plotly.offline import plot
from plotly.graph_objs import Scatter
import requests

app = Flask(__name__)

@app.route('/')
def home():
    """Displays main page"""
    try:
        response = requests.get('http://magicseaweed.com/api/e53638829bea94ae3a45213abb63a7ad/forecast/?spot_id=398').json()
    except Exception as e:
        return "<h2>Unable to retrieve swell data: {}</h2>".format(e)

    item = response[0]
    return render_template('index.html', item=item)

if __name__ == '__main__':
    app.run(debug=True)