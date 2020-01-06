from flask import Flask, render_template
from plotly.offline import plot
from plotly.graph_objs import Scatter

app = Flask(__name__)

@app.route('/')
def home():
    """Displays main page"""
    my_plot_div = plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])], output_type='div')
    return render_template('index.html', my_plot_div=my_plot_div)

if __name__ == '__main__':
    app.run(debug=True)

