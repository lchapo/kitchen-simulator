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
    spend_by_day_and_service,
    spend_by_time_of_day,
    total_spend,
)

app = dash.Dash(__name__)
server = app.server

# how frequently to refresh the data
REFRESH_INTERVAL_SECONDS = 5

app_layout = [
    html.H4('Simulation Live Dashboard'),
    html.H6(id='sim-time', style={'color': '#00FFFF'}),
    html.Div(
        [
            dcc.Graph(
                id='time-graph',
                style={'display': 'inline-block', 'height': '40vh', 'width': '68vw', 'margin-right': '1vw'},
            ),
            dcc.Graph(
                id='avg-order-time',
                style={'display': 'inline-block', 'height': '40vh', 'width': '29vw'},
            ),
        ],
        style={'width': '100%', 'margin-left': '1vw', 'margin-right': '1vw'}
    ),
    html.Div(
        [
            dcc.Graph(
                id='stacked-bar-chart',
                style={'display': 'inline-block', 'height': '40vh', 'width': '44vw', 'margin-right': '1vw'},
            ),
            dcc.Graph(
                id='total-spend',
                style={'display': 'inline-block', 'height': '40vh', 'width': '23vw', 'margin-right': '1vw'},
            ),
            dcc.Graph(
                id='pie-chart',
                style={'display': 'inline-block', 'height': '40vh', 'width': '29vw'},
            ),
        ],
        style={'width': '100%', 'margin-left': '1vw', 'margin-right': '1vw','margin-top': '1vw', 'margin-bottom': '1vw'}
    ),
    dcc.Interval(
        id='interval-component',
        interval=REFRESH_INTERVAL_SECONDS * 1000, # in milliseconds
        n_intervals=0
    )
]

app.layout = html.Div(app_layout)

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
            {'x': df.index, 'y': df['Queued'], 'type': 'line', 'name': 'Queued', 'line': {'color': '#f4d44d', 'width': '3'}},
            {'x': df.index, 'y': df['In Progress'], 'type': 'line', 'name': 'In Progress', 'line': {'color': '#00FFFF', 'width': '3'}},
        ],
        'layout': {
            'title': {'text': 'Order Statuses Over Time (PST)', 'xanchor': 'center', 'x': 0.5},
            'plot_bgcolor': '#161A28',
            'paper_bgcolor': '#161A28',
            'font': {'color': 'white', 'size': 16},
            'yaxis': {'showgrid': False, 'title': '# Orders'},
        }
    }

    return fig


@app.callback(Output('pie-chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_pie_chart(n):
    df = spend_by_time_of_day()
    fig = px.pie(df, values="total_spent", names="time_of_day")
    fig.update_traces(
        textfont_size=16,
        marker=dict(line=dict(color='white', width=1))
    )
    fig['layout'] = {
        'title': {'text': 'Revenue by Time of Day', 'xanchor': 'center', 'x': 0.5},
        'plot_bgcolor': '#161A28',
        'paper_bgcolor': '#161A28',
        'font': {'color': 'white', 'size': 16},
    }

    return fig


@app.callback(Output('stacked-bar-chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_stacked_bar_chart(n):
    df = spend_by_day_and_service()
    df['dow'] = df['dow'].map({
        0: 'Sun',
        1: 'Mon',
        2: 'Tues',
        3: 'Wed',
        4: 'Thurs',
        5: 'Fri',
        6: 'Sat',
    })
    fig = px.bar(
        df, x='dow', y='total_spent', color='service'
    )
    fig['layout'] = {
        'title': {'text': 'Revenue by Day', 'xanchor': 'center', 'x': 0.5},
        'plot_bgcolor': '#161A28',
        'paper_bgcolor': '#161A28',
        'font': {'color': 'white', 'size': 16},
        'barmode': 'stack',
        'yaxis': {'showgrid': False},
        'font': {'color': 'white', 'size': 16},
        'legend': {'traceorder': 'reversed'},
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
    layout= {
        'title': {'text': 'Total Revenue', 'xanchor': 'center', 'x': 0.5},
        'plot_bgcolor': '#161A28',
        'paper_bgcolor': '#161A28',
        'font': {'color': 'white', 'size': 16},
    }

    fig = {'data': data, 'layout': layout}

    return fig


@app.callback(Output('avg-order-time', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_avg_order_time(n):
    avg_order_time = recent_order_times()[0]
    if avg_order_time <= 40:
        font_color = '#5ceda5'
    elif avg_order_time <= 80:
        font_color = '#F4D44D'
    else:
        font_color = '#F45060'
    data= [{
        'type': 'indicator',
        'mode': 'number+gauge',
        'value': avg_order_time,
        'number': {'valueformat': '.0f', 'suffix': 'm', 'font': {'color': font_color}},
        'gauge': {
            'shape': 'gauge',
            'bar': {'color': 'darkgrey'},
            'axis': {'range': [0, 120]},
            'steps': [
                {'range': [0, 40], 'color': '#5ceda5'},
                {'range': [40, 80], 'color': '#F4D44D'},
                {'range': [80, 120], 'color': '#F45060'},
            ],
        }
    }]
    layout= {
        'title': {'text': 'Avg Recent Order Fulfillment Time', 'xanchor': 'center', 'x': 0.5},
        'plot_bgcolor': '#161A28',
        'paper_bgcolor': '#161A28',
        'font': {'color': 'white', 'size': 16},
    }
    fig = {'data': data, 'layout': layout}

    return fig


if __name__ == '__main__':
    # give simulator time to kick off
    time.sleep(3)
    app.run_server(host='0.0.0.0', port=8050)
