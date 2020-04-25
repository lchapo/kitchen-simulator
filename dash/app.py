#!/usr/bin python

from datetime import datetime

import dash
import dash_core_components as dcc
from dash.dependencies import (
    Input,
    Output,
)   
import dash_html_components as html

from sql import (
    orders_by_status,
)

app = dash.Dash(__name__)
server = app.server

# how frequently to refresh the data
REFRESH_INTERVAL_SECONDS = 5

app.layout = html.Div(
    html.Div(
        [
            html.H4('Simulation Live Dashboard'),
            html.Div(id='live-update-text'),
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=REFRESH_INTERVAL_SECONDS * 1000, # in milliseconds
                n_intervals=0
            )
        ],
    )
)

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_time(n):
    return f"Simulation Time: {str(datetime.now())}"


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    df = orders_by_status()
    fig={
        'data': [
            {'x': df['status'], 'y': df['cnt'], 'type': 'bar'},
        ],
        'layout': {
            'title': 'Current Orders by Status',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'white'},
            'yaxis': {'showgrid': False},
        }
    }

    return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
