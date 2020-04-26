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
    recent_order_times,
    max_timestamp,
    orders_by_status,
    spend_by_time_of_day,
    total_spend,
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
            dcc.Graph(id='pie-chart'),
            dcc.Graph(id='total-spend'),
            dcc.Graph(id='avg-order-time'),
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
    ts = max_timestamp()[0]
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


@app.callback(Output('pie-chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_pie_chart(n):
    df = spend_by_time_of_day()
    fig = px.pie(df, values="total_spent", names="time_of_day")
    fig['layout'] = {
        'title': 'Spend by Time of Day',
        'plot_bgcolor': '#161A28',
        'paper_bgcolor': '#161A28',
        'font': {'color': 'white'},
    }

    return fig


##########################
##    SINGLE NUMBERS    ##
##########################
@app.callback(Output('total-spend', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_total_spend(n):
    val = total_spend()[0]
    data= [{
        'type': 'indicator',
        'mode': 'number',
        'value': val,
    }]
    layout= {'title': 'Total Gross Revenue'}

    fig = {'data': data, 'layout': layout}

    return fig


@app.callback(Output('avg-order-time', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_avg_order_time(n):
    avg_order_time, avg_queue_time = recent_order_times()
    data= [{
        'type': 'indicator',
        'mode': 'number+gauge',
        'value': avg_order_time,
        'number': {'valueformat': '.0f', 'suffix': 'm'},
        'gauge': {
            'shape': 'gauge',
            'axis': {'range': [0, 120]},
            'steps': [
                {'range': [0, avg_queue_time], 'color': '#f4d44d', 'name': 'Queue Time', 'templateitemname': {'visible': True, 'enabled': True}},
                {'range': [avg_queue_time, avg_order_time], 'color': '#91dfd2', 'name': 'Cook Time', 'templateitemname': {'visible': True, 'enabled': True}},
            ],
        }
    }]
    layout= {'title': 'Recent Order Times (Queue | Cook)'}
    fig = {'data': data, 'layout': layout}

    return fig


if __name__ == '__main__':
    # give simulator time to kick off
    time.sleep(3)
    app.run_server(host='0.0.0.0', port=8050)
