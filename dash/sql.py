"""SQL Queries, returned in dataframes"""

import pandas as pd

from db.connection import (
    css_connection,
    css_cursor,
)


def query_to_df(sql_func):
    """Helper to run sql and return dataframe"""
    def get_df():
        sql = sql_func()
        with css_connection() as conn:
            return pd.read_sql_query(sql, conn)
    return get_df


def fetch_one(sql_func):
    """Helper to run sql and return single row"""
    def get_value():
        sql = sql_func()
        with css_cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()
    return get_value


@query_to_df
def orders_by_status():
    return """
    SELECT status
    , COUNT(*) as cnt
    FROM orders
    GROUP BY status
    ORDER BY status;
    """


@query_to_df
def all_timestamps():
    return """
    SELECT 
      received_at - 8*60*60 as received_at
    , started_at - 8*60*60 as started_at
    , completed_at - 8*60*60 as completed_at
    FROM orders;
    """


@query_to_df
def spend_by_day_and_service():
    return """
    SELECT
    service
    , cast(strftime('%w', received_at - 8*60*60, 'unixepoch') as int) as dow
    , SUM(total_price) AS total_spent
    FROM orders
    GROUP BY service, dow
    ORDER BY service, dow;
    """


@fetch_one
def max_timestamp():
    """Max timestamp to approximate simulator current time"""
    return """
    SELECT max(
        max(coalesce(received_at - 8*60*60,0))
        , max(coalesce(started_at - 8*60*60,0))
        , max(coalesce(completed_at - 8*60*60,0))
    )
    FROM orders;
    """


@fetch_one
def total_spend():
    return """
    SELECT SUM(total_price)
    FROM orders;
    """


@fetch_one
def recent_order_times():
    return """
    SELECT AVG(completed_at - received_at) / 60 as avg_order_time
    FROM orders
    WHERE id in (
        SELECT id
        FROM orders
        WHERE status = 'Completed'
        ORDER BY completed_at DESC
        LIMIT 50
    ) --limit to most recent 50 completed orders
    AND completed_at >= (
        SELECT max(completed_at) - 60
        FROM orders
    ) --limit to past hour
    ;
    """


@query_to_df
def spend_by_time_of_day():
    return """
    SELECT
    CASE
        WHEN cast(strftime('%H', received_at - 8*60*60, 'unixepoch') as int)
          BETWEEN 5 AND 10 THEN 'Breakfast'
        WHEN cast(strftime('%H', received_at - 8*60*60, 'unixepoch') as int)
          BETWEEN 11 AND 15 THEN 'Lunch'
        WHEN cast(strftime('%H', received_at - 8*60*60, 'unixepoch') as int)
          BETWEEN 16 AND 22 THEN 'Dinner'
        ELSE 'Late Night'
        END as time_of_day
    , SUM(total_price) AS total_spent
    FROM orders
    GROUP BY time_of_day
    ORDER BY time_of_day ASC;
    """
