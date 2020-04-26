#!/usr/bin python

from datetime import datetime
import time

import dash
import dash_core_components as dcc
from dash.dependencies import (
    Input,
    Output,
)   
import dash_html_components as html
import pandas as pd
import plotly.express as px
import numpy as np

from sql import (
    all_timestamps,
    max_timestamp,
    orders_by_status,
    spend_by_service,
)

app = dash.Dash(__name__)
server = app.server

# how frequently to refresh the data
REFRESH_INTERVAL_SECONDS = 5

app.layout = html.Div(
    html.Div(
        [
            html.H4('Simulation Live Dashboard'),
            html.Div(id='sim-time'),
            dcc.Graph(id='time-graph'),
            dcc.Graph(id='spend-by-service'),
            dcc.Interval(
                id='interval-component',
                interval=REFRESH_INTERVAL_SECONDS * 1000, # in milliseconds
                n_intervals=0
            )
        ],
    )
)

@app.callback(Output('sim-time', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_time(n):
    ts = max_timestamp()
    formatted_ts = datetime.fromtimestamp(ts).strftime('%a %m/%d %I:%M%p PST')
    formatted_ts = formatted_ts.replace(" 0", " ")
    return f"Simulation Time: {formatted_ts}"


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

    df = pd.DataFrame(
        data={'Queued': queued, 'In Progress': in_progress},
        index=pd.to_datetime(timestamps, unit='s'),
    )

    fig={
        'data': [
            {'x': df.index, 'y': df['Queued'], 'type': 'line', 'name': 'Queued', 'line': {'color': '#f4d44d'}},
            {'x': df.index, 'y': df['In Progress'], 'type': 'line', 'name': 'In Progress', 'line': {'color': '#91dfd2'}},
        ],
        'layout': {
            'title': 'Order Statuses Over Time (PST)',
            'plot_bgcolor': '#161A28',
            'paper_bgcolor': '#161A28',
            'font': {'color': 'white'},
            'yaxis': {'showgrid': False},
        }
    }

    return fig


@app.callback(Output('spend-by-service', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    df = spend_by_service()
    fig = px.bar(df, x="time_of_day", y="total_spent", color="service")
    fig['layout'] = {
        'title': 'Total Spend by Service and Meal',
        'plot_bgcolor': '#161A28',
        'paper_bgcolor': '#161A28',
        'font': {'color': 'white'},
        'yaxis': {'showgrid': False},
        'barmode': 'stack',
    }

    return fig


if __name__ == '__main__':
    time.sleep(3)
    app.run_server(host='0.0.0.0', port=8050)
