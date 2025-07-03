# dash_app.py

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from app.model import predicted_values, actual_values, time_ticks

# Create Dash instance WITHOUT calling run()
dash_app = Dash(__name__, requests_pathname_prefix='/dashboard/')

dash_app.layout = html.Div([
    html.H3("🔴 Real-time Load Curve", style={"textAlign": "center"}),
    dcc.Graph(id='live-graph', style={"height": "80vh"}),
    dcc.Interval(id='interval', interval=1000, n_intervals=0)
])

@dash_app.callback(
    Output('live-graph', 'figure'),
    Input('interval', 'n_intervals')
)
def update_graph(n):
    return {
        'data': [
            go.Scatter(x=time_ticks[:n], y=predicted_values[:n], name='Predicted', line=dict(color='blue')),
            go.Scatter(x=time_ticks[:n], y=actual_values[:n], name='Actual', line=dict(color='red'))
        ],
        'layout': go.Layout(
            xaxis={'title': 'Time'},
            yaxis={'title': 'Power Consumption'},
            height=600
        )
    }

# We expose the server object so FastAPI can mount it
dash_server = dash_app.server
