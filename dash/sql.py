"""SQL Queries, returned in dataframes"""

import pandas as pd

from connection import css_connection

def query_to_df(sql):
    """Helper to run sql and return dataframe"""
    with css_connection() as conn:
        return pd.read_sql_query(sql, conn)

def orders_by_status():
    """Query SQLite, Return dataframe"""
    sql = """
    SELECT status
    , COUNT(*) as cnt
    FROM orders
    GROUP BY status
    ORDER BY status;
    """
    return query_to_df(sql)
