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
      received_at
    , started_at
    , completed_at
    FROM orders;
    """

def max_timestamp():
    sql = """
    SELECT max(
        max(coalesce(received_at,0))
        , max(coalesce(started_at,0))
        , max(coalesce(completed_at,0))
    )
    FROM orders;
    """
    with css_cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()[0]
