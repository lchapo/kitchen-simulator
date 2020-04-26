#!/usr/bin python

from datetime import datetime

import dash
import dash_core_components as dcc
from dash.dependencies import (
    Input,
    Output,
)   
import dash_html_components as html
import pandas as pd
import numpy as np

from sql import (
    all_timestamps,
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
            dcc.Graph(id='time-graph'),
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


@app.callback(Output('time-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_time_graph(n):
    df = all_timestamps()
    start = int(min(df['received_at']))
    end = int(max(np.concatenate([
        df["received_at"].values,
        df["started_at"].fillna(0).values,
        df["completed_at"].fillna(0).values,
    ])))

    # calculate status counts at different time frames
    timestamps = [ts for ts in range(start, end, 600)]
    queued = [(
        (df['received_at'].values <= ts) &
        (ts < df['started_at'].fillna(np.inf).values)
    ).sum() for ts in timestamps]
    # in progress: started but not yet completed
    in_progress = [(
        (df['started_at'].fillna(np.inf).values <= ts) &
        (ts < df['completed_at'].fillna(np.inf).values)
    ).sum() for ts in timestamps]
    # completed
    completed = [
        (ts >= df['completed_at'].fillna(np.inf).values).sum()
        for ts in timestamps
    ]

    df = pd.DataFrame(
        data={'Queued': queued, 'In Progress': in_progress, 'Completed': completed},
        index=pd.to_datetime(timestamps, unit='s'),
    )

    fig={
        'data': [
            {'x': df.index, 'y': df['Queued'], 'type': 'line', 'name': 'Queued'},
            {'x': df.index, 'y': df['In Progress'], 'type': 'line', 'name': 'In Progress'},
            {'x': df.index, 'y': df['Completed'], 'type': 'line', 'name': 'Completed'},
        ],
        'layout': {
            'title': 'Order Statuses Over Time',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'white'},
            'yaxis': {'showgrid': False},
        }
    }

    return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
