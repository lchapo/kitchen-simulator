"""SQL Queries, returned in dataframes"""

import pandas as pd

from connection import css_connection


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
