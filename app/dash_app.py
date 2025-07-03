from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from app.model import predicted_values, actual_values, time_ticks
import os

def launch_dash_app():
    app = Dash(__name__)
    server = app.server

    app.layout = html.Div([
        html.H3("🔴 Real-time Load Curve", style={"textAlign": "center"}),
        dcc.Graph(id='live-graph', style={"height": "80vh"}),
        dcc.Interval(id='interval', interval=1000, n_intervals=0)
    ])

    @app.callback(
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    launch_dash_app()
