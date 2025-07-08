from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

def create_dash_app(shared_state):
    dash_app = Dash(__name__, routes_pathname_prefix="/dashboard/")
    server = dash_app.server

    dash_app.layout = html.Div([
        html.H2("📈 Real-time Power Consumption Prediction"),
        html.H4(id='selected-date-display', style={'marginTop': '10px'}),
        dcc.Graph(id='live-graph'),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
    ])

    @dash_app.callback(Output('live-graph', 'figure'), Input('interval-component', 'n_intervals'))
    def update_graph(_):
        return {
            'data': [
                go.Scatter(x=shared_state["timestamps"], y=shared_state["predicted_values"], name='Predicted', line=dict(color='blue')),
                go.Scatter(x=shared_state["timestamps"], y=shared_state["actual_values"], name='Actual', line=dict(color='red'))
            ],
            'layout': go.Layout(
                xaxis={'title': 'Time'},
                yaxis={'title': 'Power Consumption'},
                height=600
            )
        }

    @dash_app.callback(Output('selected-date-display', 'children'), Input('interval-component', 'n_intervals'))
    def update_date_display(_):
        return f"📅 Forecast for: {shared_state['selected_date']}" if shared_state['selected_date'] else ""

    return server
