#!/usr/bin python

from datetime import datetime
import os
import pathlib

import dash
import dash_core_components as dcc
from dash.dependencies import (
    Input,
    Output,
    State,
)   
import dash_html_components as html
import numpy as np
import pandas as pd

from common import (
    css_connection,
    css_cursor,
    execute_sql,
)

app = dash.Dash(__name__)
server = app.server

SQL = """
SELECT status
, COUNT(*) as cnt
FROM orders
GROUP BY status
ORDER BY status
"""

def get_fresh_data():
    """Query SQLite, Return dataframe"""
    with css_connection() as conn:
        return pd.read_sql_query(SQL, conn)

app.layout = html.Div(
    html.Div([
        html.H4('Current Order Status'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=5000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_time(n):
    return f"Simulation Time: {str(datetime.now())}"


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    df = get_fresh_data()
    fig={
        'data': [
            {'x': df['status'], 'y': df['cnt'], 'type': 'bar'},
        ],
        'layout': {
            'title': 'Dash Data Visualization'
        }
    }

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
